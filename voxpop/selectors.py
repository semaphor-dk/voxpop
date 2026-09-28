from __future__ import annotations  # For Python3.9 users.

from uuid import UUID

from django.db.models import BooleanField
from django.db.models import Case
from django.db.models import Count
from django.db.models import QuerySet
from django.db.models import When
from django.http import HttpRequest
from django.utils import timezone

from voxpop.models import Message
from voxpop.models import Organisation
from voxpop.models import Question
from voxpop.models import Vote
from voxpop.models import Voxpop


def current_organisation(request: HttpRequest) -> Organisation | None:
    try:
        return Organisation.objects.get(hostname=request.get_host())
    except Organisation.DoesNotExist:
        return None


def get_voxpops(organisation) -> QuerySet[Voxpop]:
    now = timezone.now()
    voxpops = organisation.voxpops.all().annotate(
        question_count=Count("questions", distinct=True),
        is_active=Case(
            When(
                starts_at__lte=now,
                expires_at__gte=now,
                then=True,
            ),
            default=False,
            output_field=BooleanField(),
        ),
    )
    return voxpops


def get_voxpop(voxpop_id) -> Voxpop:
    now = timezone.now()
    voxpop = (
        Voxpop.objects.filter(uuid=voxpop_id)
        .annotate(
            question_count=Count("questions", distinct=True),
            is_active=Case(
                When(
                    starts_at__lte=now,
                    expires_at__gte=now,
                    then=True,
                ),
                default=False,
                output_field=BooleanField(),
            ),
        )
        .first()
    )
    return voxpop


def get_questions(
    voxpop: Voxpop,
    state: Question.State | None = None,
) -> QuerySet[Question] | None:
    questions = voxpop.questions.all().annotate(
        vote_count=Count("votes", distinct=True),
    )
    # First do all filtering
    if state:
        questions = questions.filter(state=state)
    return questions


def get_votes(
    vote_id: UUID | None = None,
    question_id: UUID | None = None,
    voxpop_id: UUID | None = None,
) -> QuerySet[Vote] | Vote:
    votes = Vote.objects.all()

    if voxpop_id:
        votes = votes.filter(question__voxpop_id=voxpop_id)

    if question_id:
        votes = votes.filter(question_id=question_id)

    if vote_id:
        return votes.get(uuid=vote_id)

    return votes


async def get_messages(channel_name: str, last_event_id: int) -> list[Message]:
    messages = []
    async for message in (
        Message.objects.all()
        .filter(
            channel_name=channel_name,
            id__gt=last_event_id,
        )
        .order_by("id")
    ):
        messages.append(message)
    return messages
