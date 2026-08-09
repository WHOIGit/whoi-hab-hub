from django.apps import AppConfig


class IfcbDatasetsConfig(AppConfig):
    name = "habhub.ifcb_datasets"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        # Connect signals by importing the file
        import habhub.ifcb_datasets.signals
