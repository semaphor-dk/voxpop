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
            "uuid": str(instance.uuid),
            "text": str(instance.text),
        }

        notify(
            channel_name=channel_name,
            payload=f"event: new_question\ndata: {json.dumps(payload)}",
        )


@receiver(post_save, sender=Vote)
def notify_vote_created(sender, instance, created, **kwargs):
    if created:
        channel_name = get_notify_channel_name(voxpop_id=instance.question.voxpop_id)

        payload = {
            "question_id": str(instance.question_id),
            "vote_count": instance.question.votes.count(),
        }

        notify(
            channel_name=channel_name,
            payload=f"event: new_vote\ndata: {json.dumps(payload)}",
        )
