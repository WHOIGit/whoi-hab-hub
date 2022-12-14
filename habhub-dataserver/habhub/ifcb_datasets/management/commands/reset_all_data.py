from django.core.management.base import BaseCommand, CommandError
from habhub.ifcb_datasets.tasks import reset_ifcb_dataset_data


class Command(BaseCommand):
    help = "Reset all IFCB data. This will clear all current IFCB data from database"

    def handle(self, *args, **options):
        try:
            reset_ifcb_dataset_data.delay()
        except:
            raise CommandError("ERROR resetting data. Check docker container logs")

        self.stdout.write(
            self.style.SUCCESS("Successfully started data reset for all IFCB datasets")
        )
