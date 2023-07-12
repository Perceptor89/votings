from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver
from .models import Character
from django.conf import settings


@receiver(pre_delete, sender=Character)
def character_image_delete(sender, instance, **kwargs):
    if instance.photo.name:
        if not settings.TESTING:
            try:
                instance.photo.delete()
            except Exception:
                pass
