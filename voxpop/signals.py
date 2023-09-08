import json

from django.db.models.signals import pre_save
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Question
from .models import Vote
from .services import create_message
from .utils import get_notify_channel_name
from .utils import notify


@receiver(pre_save, sender=Question)
def notify_question_state_changed(sender, instance, *args, **kwargs):
    original_state = None
    if instance.created_at != None:
        original_state = Question.objects.get(pk=instance.uuid).state
        if instance.state != original_state:
            if instance.state == Question.State.APPROVED:
                channel_name = get_notify_channel_name(voxpop_id=instance.voxpop_id)
                payload = {
                    "uuid": str(instance.uuid),
                    "text": str(instance.text),
                    "display_name": str(instance.display_name),
                    "created_at": "tid ..."
                }
                message=create_message(
                    voxpop_id=instance.voxpop_id,
                    event="new_question",
                    data=json.dumps(payload)
                )
                notify(channel_name=channel_name, payload=message)
            admin_channel_name = get_notify_channel_name(channel_prefix="admin_", voxpop_id=instance.voxpop_id)
            payload = {
                "question_id": str(instance.uuid),
                "state": instance.state
            }
            message = create_message(
                voxpop_id=instance.voxpop_id,
                event="question_state_update",
                data=json.dumps(payload)
            )
            notify(channel_name=admin_channel_name, payload=message)


@receiver(post_save, sender=Question)
def notify_question_created(sender, instance, created, **kwargs):
    if created:
        payload = {
            "uuid": str(instance.uuid),
            "text": str(instance.text),
            "display_name": str(instance.display_name),
            "created_at": "tid ..."
        }
        message = create_message(
            voxpop_id=instance.voxpop_id,
            event="new_question",
            data=json.dumps(payload)
        )
        if instance.state == Question.State.APPROVED:
            channel_name = get_notify_channel_name(voxpop_id=instance.voxpop_id)
            notify(channel_name=channel_name, payload=message)
        admin_channel_name = get_notify_channel_name(channel_prefix="admin_", voxpop_id=instance.voxpop_id)
        notify(channel_name=admin_channel_name, payload=message)


@receiver(post_save, sender=Vote)
def notify_vote_created(sender, instance, created, **kwargs):
    if created:
        payload = {
            "question_id": str(instance.question_id),
            "vote_count": instance.question.votes.count()
        }
        message = create_message(
            voxpop_id=instance.question.voxpop_id,
            event="new_vote",
            data=json.dumps(payload)
        )
        channel_name = get_notify_channel_name(voxpop_id=instance.question.voxpop_id)
        notify(channel_name=channel_name, payload=message)
        admin_channel_name = get_notify_channel_name(channel_prefix="admin_", voxpop_id=instance.question.voxpop_id)
        notify(channel_name=admin_channel_name, payload=message)
