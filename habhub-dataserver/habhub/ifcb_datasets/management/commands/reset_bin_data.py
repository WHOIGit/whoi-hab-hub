import datetime
from django.utils import timezone
from django.core.management.base import BaseCommand, CommandError
from habhub.ifcb_datasets.models import Dataset, Bin


class Command(BaseCommand):
    help = "Reset all IFCB data for a specific Dataset. Args: --datasets Enter the Dashboard ID names as an argument, separate with + sign for multiple datasets. Enter optional --start_date and --end_date range in yyyy-mm-dd format"

    def add_arguments(self, parser):
        parser.add_argument("--datasets", nargs="+", type=str)
        parser.add_argument("--start_date", nargs="?", type=str, const="")
        parser.add_argument("--end_date", nargs="?", type=str, const="")

    def handle(self, *args, **options):
        start_date = options["start_date"]
        end_date = options["end_date"]

        for dataset_name in options["datasets"]:
            try:
                dataset = Dataset.objects.get(dashboard_id_name=dataset_name)
            except Dataset.DoesNotExist:
                raise CommandError('Dataset "%s" does not exist' % dataset_name)

            try:
                earliest_bin = Bin.objects.earliest()
            except Bin.DoesNotExist:
                return "Error. No Bins exist."

            if start_date:
                start_date_obj = datetime.datetime.strptime(
                    start_date, "%Y-%m-%d"
                ).date()
            else:
                start_date_obj = earliest_bin.sample_time

            if end_date:
                end_date_obj = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
            else:
                end_date_obj = timezone.now()
            print("Dates: ", start_date_obj, end_date_obj)
            dataset.reset_bin_data(start_date_obj, end_date_obj)

            self.stdout.write(
                self.style.SUCCESS(
                    'Successfully started data reset for "%s"' % dataset_name
                )
            )
