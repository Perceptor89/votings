from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
from .models import Character


@receiver(pre_delete, sender=Character)
def image_model_delete(sender, instance, **kwargs):
    if instance.photo.name:
        instance.photo.delete(False)
