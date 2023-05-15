import json

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Question
from .models import Vote
from .utils import get_notify_channel_name
from .utils import notify


@receiver(post_save, sender=Question)
def notify_question_created(sender, instance, created, **kwargs):
    if created:
        channel_name = get_notify_channel_name(voxpop_id=instance.voxpop_id)

        payload = {
            "type": "question_created",
            "question": {
                "id": str(instance.uuid),
                "text": str(instance.text),
            },
        }

        notify(
            channel_name=channel_name,
            payload=json.dumps(payload),
        )


@receiver(post_save, sender=Vote)
def notify_vote_created(sender, instance, created, **kwargs):
    if created:
        channel_name = get_notify_channel_name(voxpop_id=instance.voxpop_id)

        payload = {
            "type": "vote_created",
            "vote": {
                "id": str(instance.uuid),
                "question_id": str(instance.question_id),
            },
        }

        notify(
            channel_name=channel_name,
            payload=json.dumps(payload),
        )
