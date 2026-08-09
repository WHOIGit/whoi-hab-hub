# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from .models import Dataset
from .tasks import reset_ifcb_dataset_data

@receiver(post_save, sender=Dataset)
def order_created_signal(sender, instance, created, **kwargs):
    # Only run the task when the object is freshly created
    if created:
        transaction.on_commit(lambda: reset_ifcb_dataset_data.delay(instance.id))
