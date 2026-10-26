import datetime
import time
from concurrent.futures import ThreadPoolExecutor
from django.core.management.base import BaseCommand, CommandError
from opensearchpy import helpers
from opensearchpy.exceptions import TransportError
from habhub.core.models import TargetSpecies
from habhub.ifcb_datasets.api2.views import connect_opensearch
from habhub.ifcb_datasets.opensearch import (
    SCORES_INDEX_NAME,
    SUMMARY_INDEX_NAME,
    build_image_fields,
    create_summary_index,
    score_bucket,
)

# max bulk request size. Each partial update re-indexes the whole (large) summary
# document, so keep the requests small to avoid the cluster's memory circuit breaker
MAX_CHUNK_BYTES = 2 * 1024 * 1024
CHUNK_SIZE = 200


def build_bin_images(os_client, start_time, end_time, species_ids):
    # read the target species image documents for the Bins sampled in the time range,
    # return {binPid: {species: {modelId: [(imageNumber, bucket), ...]}}}
    query = {
        "query": {
            "bool": {
                "must": [
                    {
                        "range": {
                            "sampleTime": {
                                "gte": start_time.isoformat(),
                                "lt": end_time.isoformat(),
                            }
                        }
                    },
                    {"terms": {"species": species_ids}},
                ]
            }
        },
        "_source": False,
        "docvalue_fields": ["binPid", "species", "modelId", "imageNumber", "score"],
    }
    bin_images = {}
    for hit in helpers.scan(
        os_client,
        query=query,
        index=SCORES_INDEX_NAME,
        # small pages, larger ones can trip the cluster's memory circuit breaker
        size=2000,
        scroll="5m",
        request_timeout=300,
        # the scroll requests after the first search use the client's 20 second
        # default timeout otherwise
        scroll_kwargs={"request_timeout": 300},
    ):
        fields = hit["fields"]
        bin_images.setdefault(fields["binPid"][0], {}).setdefault(
            fields["species"][0], {}
        ).setdefault(fields["modelId"][0], []).append(
            (int(fields["imageNumber"][0]), score_bucket(fields["score"][0]))
        )
    return bin_images


def update_summary_images(os_client, bin_images):
    # add the "i" fields to the Bin summary documents
    operations = (
        {
            "_op_type": "update",
            "_index": SUMMARY_INDEX_NAME,
            "_id": bin_pid,
            "retry_on_conflict": 10,
            "doc": {"i": build_image_fields(species_images)},
        }
        for bin_pid, species_images in bin_images.items()
    )
    return helpers.bulk(
        os_client,
        operations,
        chunk_size=CHUNK_SIZE,
        max_chunk_bytes=MAX_CHUNK_BYTES,
        max_retries=3,
        request_timeout=300,
        # skip Bins without a summary document yet, the ingest Lambda adds them
        raise_on_error=False,
    )


class Command(BaseCommand):
    # ex: python manage.py backfill_summary_images --start_date=2025-01-01 --end_date=2026-01-01
    help = "Add the 'i' image doc value fields for the TargetSpecies to 'bin-species-summary' documents from the 'species-scores' index. Args: --start_date and --end_date range in yyyy-mm-dd format, optional --species to backfill these species IDs instead of the TargetSpecies (separate with commas), optional --workers to set the number of months processed in parallel (default 2)"

    def add_arguments(self, parser):
        parser.add_argument("--start_date", type=str, required=True)
        parser.add_argument("--end_date", type=str, required=True)
        parser.add_argument("--species", type=str, default=None)
        parser.add_argument("--workers", type=int, default=2)

    def handle(self, *args, **options):
        try:
            start_date = datetime.datetime.strptime(options["start_date"], "%Y-%m-%d")
            end_date = datetime.datetime.strptime(options["end_date"], "%Y-%m-%d")
        except ValueError:
            raise CommandError("Dates must be in yyyy-mm-dd format")

        # the species to backfill, the TargetSpecies by default. Pass --species to
        # backfill one new species, or when the database running the command doesn't
        # have the production TargetSpecies
        if options["species"]:
            species_ids = options["species"].split(",")
        else:
            species_ids = list(TargetSpecies.objects.values_list("species_id", flat=True))
        if not species_ids:
            raise CommandError("No TargetSpecies to backfill")
        self.stdout.write(f"Species: {', '.join(species_ids)}")

        os_client = connect_opensearch()
        # adds the "i" mapping to the existing index
        create_summary_index(os_client)

        # month start dates in the range
        months = []
        month_start = start_date.replace(day=1)
        while month_start < end_date:
            months.append(month_start)
            month_start = (month_start + datetime.timedelta(days=32)).replace(day=1)

        def backfill_month(month_start):
            month_end = min((month_start + datetime.timedelta(days=32)).replace(day=1), end_date)
            month_start = max(month_start, start_date)
            bin_images = self.retry(
                lambda: build_bin_images(os_client, month_start, month_end, species_ids)
            )
            updated, errors = self.retry(lambda: update_summary_images(os_client, bin_images))
            missing = len(errors) if isinstance(errors, list) else errors
            self.stdout.write(
                f"{month_start.strftime('%Y-%m')}: {updated} Bins updated"
                + (f", {missing} without a summary document" if missing else "")
            )
            return updated

        with ThreadPoolExecutor(max_workers=options["workers"]) as executor:
            total_bins = sum(executor.map(backfill_month, months))

        self.stdout.write(self.style.SUCCESS(f"Done. {total_bins} Bins updated"))

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
