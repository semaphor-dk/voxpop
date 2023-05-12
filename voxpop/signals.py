import psycopg
from django.db import connection
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Question
from .utils import get_notify_channel_name


@receiver(post_save, sender=Question)
def notify_question_created(sender, instance, created, **kwargs):
    if created:
        print("New question created")
        conn = psycopg.connect(
            **connection.get_connection_params(),
            autocommit=True,
        )
        channel_name = get_notify_channel_name(voxpop_id=instance.voxpop_id)
        with conn.cursor() as cursor:
            cursor.execute(
                f"NOTIFY {channel_name}, '{instance.uuid} {instance.text}'",
            )
