import datetime
import time
from concurrent.futures import ThreadPoolExecutor
from django.core.management.base import BaseCommand, CommandError
from opensearchpy import helpers
from opensearchpy.exceptions import TransportError
from habhub.ifcb_datasets.api2.views import connect_opensearch
from habhub.ifcb_datasets.opensearch import (
    SCORES_INDEX_NAME,
    SUMMARY_INDEX_NAME,
    build_histogram_fields,
    create_summary_index,
)

# max bulk request size, AWS Opensearch limits requests to 10MB on smaller instances
MAX_CHUNK_BYTES = 5 * 1024 * 1024


# offset for the score histogram buckets, see score_bucket() in the ingest Lambda
SCORE_BUCKET_OFFSET = 0.000001


class TooManyBucketsError(Exception):
    pass


def get_months_with_data(os_client, start_time, end_time):
    # get the start of each month that has image scores so empty periods can be skipped
    query = {
        "size": 0,
        "track_total_hits": False,
        "query": {
            "range": {
                "sampleTime": {
                    "gte": start_time.isoformat(),
                    "lt": end_time.isoformat(),
                }
            }
        },
        "aggs": {
            "months": {
                "date_histogram": {
                    "field": "sampleTime",
                    "calendar_interval": "month",
                    "min_doc_count": 1,
                }
            }
        },
    }
    response = os_client.search(
        body=query, index=SCORES_INDEX_NAME, request_timeout=300
    )
    return [
        datetime.datetime.fromtimestamp(bucket["key"] / 1000, datetime.UTC).replace(
            tzinfo=None
        )
        for bucket in response["aggregations"]["months"]["buckets"]
    ]


def build_summary_documents(os_client, start_time, end_time):
    # aggregate the image scores for all Bins sampled in the time range into
    # one summary document per Bin with image counts per species per model
    query = {
        "size": 0,
        "track_total_hits": False,
        "query": {
            "range": {
                "sampleTime": {
                    "gte": start_time.isoformat(),
                    "lt": end_time.isoformat(),
                }
            }
        },
        "aggs": {
            "bin-agg": {
                "terms": {"field": "binPid", "size": 10000},
                "aggs": {
                    "metadata": {
                        "top_hits": {
                            "_source": [
                                "datasetId",
                                "sampleTime",
                                "point",
                                "mlAnalyzed",
                            ],
                            "size": 1,
                        }
                    },
                    "model-agg": {
                        "terms": {"field": "modelId", "size": 100},
                        "aggs": {
                            "species-agg": {
                                "terms": {"field": "species", "size": 1000},
                                "aggs": {
                                    # 0.01 wide score histogram. The offset matches
                                    # score_bucket() in the ingest Lambda so float32
                                    # scores like 0.7 land in the same bucket
                                    "score-agg": {
                                        "histogram": {
                                            "field": "score",
                                            "interval": 0.01,
                                            "offset": -SCORE_BUCKET_OFFSET,
                                            "min_doc_count": 1,
                                        }
                                    }
                                },
                            }
                        },
                    },
                },
            }
        },
    }
    response = os_client.search(
        body=query, index=SCORES_INDEX_NAME, request_timeout=300
    )
    bin_agg = response["aggregations"]["bin-agg"]
    if bin_agg["sum_other_doc_count"]:
        raise TooManyBucketsError(f"Too many Bins between {start_time} and {end_time}")

    date_updated = datetime.datetime.now().isoformat()
    documents = []
    for bin_bucket in bin_agg["buckets"]:
        metadata = bin_bucket["metadata"]["hits"]["hits"][0]["_source"]
        species_counts = {}
        species_scores = {}
        model_ids = []
        for model_bucket in bin_bucket["model-agg"]["buckets"]:
            model_ids.append(model_bucket["key"])
            for species_bucket in model_bucket["species-agg"]["buckets"]:
                species_counts.setdefault(species_bucket["key"], {})[
                    model_bucket["key"]
                ] = species_bucket["doc_count"]
                histogram = {}
                for score_bucket in species_bucket["score-agg"]["buckets"]:
                    bucket = min(
                        round((score_bucket["key"] + SCORE_BUCKET_OFFSET) * 100), 99
                    )
                    histogram[bucket] = (
                        histogram.get(bucket, 0) + score_bucket["doc_count"]
                    )
                species_scores.setdefault(species_bucket["key"], {})[
                    model_bucket["key"]
                ] = sorted([bucket, count] for bucket, count in histogram.items())

        documents.append(
            {
                "binPid": bin_bucket["key"],
                "datasetId": metadata["datasetId"],
                "sampleTime": metadata["sampleTime"],
                "point": metadata["point"],
                "mlAnalyzed": metadata["mlAnalyzed"],
                "modelIds": model_ids,
                "speciesCounts": species_counts,
                "speciesScores": species_scores,
                "h": build_histogram_fields(species_scores),
                "dateUpdated": date_updated,
            }
        )

    return documents


def index_summary_documents(os_client, documents):
    operations = [
        {
            "_op_type": "index",
            "_index": SUMMARY_INDEX_NAME,
            "_id": document["binPid"],
            "_source": document,
        }
        for document in documents
    ]
    return helpers.bulk(
        os_client,
        operations,
        max_chunk_bytes=MAX_CHUNK_BYTES,
        max_retries=3,
        request_timeout=120,
    )


class Command(BaseCommand):
    # ex: python manage.py backfill_bin_species_summary --start_date=2025-01-01 --end_date=2026-01-01
    help = "Build the Opensearch 'bin-species-summary' index from the 'species-scores' index. Args: --start_date and --end_date range in yyyy-mm-dd format, optional --chunk_hours to set the time range aggregated per query (default 1), optional --workers to set the number of months processed in parallel (default 1)"

    def add_arguments(self, parser):
        parser.add_argument("--start_date", type=str, required=True)
        parser.add_argument("--end_date", type=str, required=True)
        parser.add_argument("--chunk_hours", type=int, default=1)
        parser.add_argument("--workers", type=int, default=1)

    def handle(self, *args, **options):
        try:
            start_date = datetime.datetime.strptime(options["start_date"], "%Y-%m-%d")
            end_date = datetime.datetime.strptime(options["end_date"], "%Y-%m-%d")
        except ValueError:
            raise CommandError("Dates must be in yyyy-mm-dd format")

        chunk = datetime.timedelta(hours=options["chunk_hours"])
        os_client = connect_opensearch()
        create_summary_index(os_client)

        def backfill_month(month_start):
            month_end = (month_start + datetime.timedelta(days=32)).replace(day=1)
            chunk_start = max(month_start, start_date)
            month_end = min(month_end, end_date)
            month_bins = 0
            while chunk_start < month_end:
                chunk_end = min(chunk_start + chunk, month_end)
                month_bins += self.backfill_chunk(os_client, chunk_start, chunk_end)
                chunk_start = chunk_end

            self.stdout.write(f"{month_start.strftime('%Y-%m')}: {month_bins} Bins")
            return month_bins

        months = get_months_with_data(os_client, start_date, end_date)
        with ThreadPoolExecutor(max_workers=options["workers"]) as executor:
            total_bins = sum(executor.map(backfill_month, months))

        self.stdout.write(self.style.SUCCESS(f"Done. {total_bins} Bins indexed"))

    def backfill_chunk(self, os_client, start_time, end_time, attempt=1):
        try:
            documents = build_summary_documents(os_client, start_time, end_time)
        except (TooManyBucketsError, TransportError) as err:
            if isinstance(err, TransportError) and "too_many_buckets" not in str(err):
                # retry errors from a busy cluster, like cancelled queries or timeouts
                if attempt >= 5:
                    raise
                self.stdout.write(
                    f"Retrying {start_time.isoformat()} - {end_time.isoformat()} after error: {err}"
                )
                time.sleep(30 * attempt)
                return self.backfill_chunk(
                    os_client, start_time, end_time, attempt + 1
                )
            # split the time range in half and try again
            if end_time - start_time <= datetime.timedelta(minutes=15):
                raise CommandError(
                    f"Too many buckets between {start_time} and {end_time}"
                )
            mid_time = start_time + (end_time - start_time) / 2
            self.stdout.write(
                f"Too many buckets, splitting {start_time.isoformat()} - {end_time.isoformat()}"
            )
            return self.backfill_chunk(
                os_client, start_time, mid_time
            ) + self.backfill_chunk(os_client, mid_time, end_time)

        if documents:
            index_summary_documents(os_client, documents)
        return len(documents)
