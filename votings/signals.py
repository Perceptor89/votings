import logging
import os

from celery.result import AsyncResult
from django.conf import settings
from django.db.models.signals import pre_delete, pre_save
from django.dispatch.dispatcher import receiver

from .models import Character, ExportTask


@receiver(pre_delete, sender=Character)
def delete_photo(sender, instance: Character, **kwargs):
    if not settings.TESTING:
        try:
            instance.img.delete(save=False)
        except Exception:
            logging.warning('Failed to delete character id '
                            f'{instance.id} photo.')


@receiver(pre_save, sender=Character)
def delete_prev_photo(sender, instance, *args, **kwargs):
    try:
        old_img = Character.objects.get(id=instance.id).photo.path
        new_img = instance.photo.path if instance.photo else None
        if new_img != old_img:
            if os.path.exists(old_img):
                os.remove(old_img)
    except Exception:
        logging.warning('Failed to delete character id '
                        f'{instance.id} previous photo.')


@receiver(pre_delete, sender=ExportTask)
def delete_result_xlsx(sender, instance: ExportTask, **kwargs):
    try:
        AsyncResult(instance.task_id).forget()
    except Exception:
        logging.warning('Failed to delete export task id '
                        f'{instance.id} celery result.')

    if instance.xlsx:
        try:
            instance.xlsx.delete(save=False)
        except Exception:
            logging.warning('Failed to delete export task id '
                            f'{instance.id} xlsx.')
