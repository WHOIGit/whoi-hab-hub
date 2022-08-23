from django.core.management.base import BaseCommand, CommandError
from habhub.ifcb_datasets.models import Dataset


class Command(BaseCommand):
    help = "Reset all IFCB data for a specific Dataset. Enter the Dashboard ID name as an argument"

    def add_arguments(self, parser):
        parser.add_argument("dataset_names", nargs="+", type=str)

    def handle(self, *args, **options):
        for dataset_name in options["dataset_names"]:
            try:
                dataset = Dataset.objects.get(dashboard_id_name=dataset_name)
            except Dataset.DoesNotExist:
                raise CommandError('Dataset "%s" does not exist' % dataset_name)

            dataset.reset_bin_data()

            self.stdout.write(
                self.style.SUCCESS(
                    'Successfully started data reset for "%s"' % dataset_name
                )
            )
