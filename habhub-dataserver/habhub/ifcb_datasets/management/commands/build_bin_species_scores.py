import datetime
import time
from concurrent.futures import ThreadPoolExecutor
from django.core.management.base import BaseCommand, CommandError
from opensearchpy import helpers
from opensearchpy.exceptions import TransportError
from habhub.ifcb_datasets.api2.views import connect_opensearch
from habhub.ifcb_datasets.opensearch import (
    SUMMARY_INDEX_NAME,
    create_summary_index,
    species_score_operations,
)

# number of Bin summary documents read per request
PAGE_SIZE = 1000


class Command(BaseCommand):
    # ex: python manage.py build_bin_species_scores --start_date=2025-01-01 --end_date=2026-01-01
    help = "Build the Opensearch 'bin-species-scores' index from the 'bin-species-summary' index. Args: --start_date and --end_date range in yyyy-mm-dd format, optional --workers to set the number of months processed in parallel (default 2)"

    def add_arguments(self, parser):
        parser.add_argument("--start_date", type=str, required=True)
        parser.add_argument("--end_date", type=str, required=True)
        parser.add_argument("--workers", type=int, default=2)

    def handle(self, *args, **options):
        try:
            start_date = datetime.datetime.strptime(options["start_date"], "%Y-%m-%d")
            end_date = datetime.datetime.strptime(options["end_date"], "%Y-%m-%d")
        except ValueError:
            raise CommandError("Dates must be in yyyy-mm-dd format")

        os_client = connect_opensearch()
        create_summary_index(os_client)

        # get the start of each month that has Bins so empty periods can be skipped
        response = os_client.search(
            index=SUMMARY_INDEX_NAME,
            body={
                "size": 0,
                "query": self.date_query(start_date, end_date),
                "aggs": {
                    "months": {
                        "date_histogram": {
                            "field": "sampleTime",
                            "calendar_interval": "month",
                            "min_doc_count": 1,
                        }
                    }
                },
            },
            request_timeout=300,
        )
        months = [
            datetime.datetime.fromtimestamp(
                bucket["key"] / 1000, datetime.UTC
            ).replace(tzinfo=None)
            for bucket in response["aggregations"]["months"]["buckets"]
        ]

        def build_month(month_start):
            month_end = (month_start + datetime.timedelta(days=32)).replace(day=1)
            month_bins, month_docs = self.build_range(
                os_client, max(month_start, start_date), min(month_end, end_date)
            )
            self.stdout.write(
                f"{month_start.strftime('%Y-%m')}: {month_bins} Bins, {month_docs} species documents"
            )
            return month_bins

        with ThreadPoolExecutor(max_workers=options["workers"]) as executor:
            total_bins = sum(executor.map(build_month, months))

        self.stdout.write(self.style.SUCCESS(f"Done. {total_bins} Bins indexed"))

    def date_query(self, start_time, end_time):
        return {
            "range": {
                "sampleTime": {
                    "gte": start_time.isoformat(),
                    "lt": end_time.isoformat(),
                }
            }
        }

    def build_range(self, os_client, start_time, end_time):
        # page through the Bin summary documents and index their species documents
        total_bins = 0
        total_docs = 0
        search_after = None
        while True:
            query = {
                "size": PAGE_SIZE,
                "track_total_hits": False,
                "sort": [{"binPid": "asc"}],
                "query": self.date_query(start_time, end_time),
                "_source": [
                    "binPid",
                    "datasetId",
                    "sampleTime",
                    "dateUpdated",
                    "point",
                    "speciesScores",
                ],
            }
            if search_after:
                query["search_after"] = search_after

            hits = self.retry(
                lambda: os_client.search(
                    index=SUMMARY_INDEX_NAME, body=query, request_timeout=300
                )["hits"]["hits"]
            )
            documents = [hit["_source"] for hit in hits]
            indexed, _ = self.retry(
                lambda: helpers.bulk(
                    os_client,
                    species_score_operations(documents),
                    chunk_size=2000,
                    max_retries=3,
                    request_timeout=300,
                )
            )
            total_bins += len(documents)
            total_docs += indexed

            if len(hits) < PAGE_SIZE:
                return total_bins, total_docs
            search_after = hits[-1]["sort"]

    def retry(self, request, attempts=5):
        # retry errors from a busy cluster, like cancelled queries or timeouts
        for attempt in range(1, attempts + 1):
            try:
                return request()
            except TransportError as err:
                if attempt == attempts:
                    raise
                self.stdout.write(f"Retrying after error: {err}")
                time.sleep(30 * attempt)
