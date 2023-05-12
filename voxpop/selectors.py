from __future__ import annotations  # For Python3.9 users.

from uuid import UUID

from django.db.models import BooleanField
from django.db.models import Case
from django.db.models import Count
from django.db.models import QuerySet
from django.db.models import When
from django.http import HttpRequest
from django.utils import timezone

from voxpop.models import Organisation
from voxpop.models import Question
from voxpop.models import Vote
from voxpop.models import Voxpop


def current_organisation(request: HttpRequest) -> Organisation | None:
    try:
        return Organisation.objects.get(hostname=request.get_host())
    except Organisation.DoesNotExist:
        return None


def get_organisations(
    organisation_id: UUID | None = None,
    hostname: str | None = None,
) -> QuerySet[Organisation] | Organisation | None:
    organisations = Organisation.objects.all()

    if hostname:
        try:
            return organisations.get(hostname=hostname)
        except Organisation.DoesNotExist:
            return None

    return organisations


def get_questions(
    question_id: UUID | None = None,
    state: Question.State | None = None,
    voxpop_id: UUID | None = None,
) -> QuerySet[Question] | Question | None:
    questions = Question.objects.all().annotate(
        vote_count=Count("votes", distinct=True),
    )

    # First do all filtering
    if state:
        questions = questions.filter(state=state)

    if voxpop_id:
        questions = questions.filter(voxpop_id=voxpop_id)

    # Then do the get if needed
    if question_id:
        try:
            return questions.get(uuid=question_id)
        except Question.DoesNotExist:
            return None

    return questions


def get_voxpops(
    voxpop_id: UUID | None = None,
    organisation_id: UUID | None = None,
) -> QuerySet[Voxpop] | Voxpop:
    now = timezone.now()
    voxpops = Voxpop.objects.all().annotate(
        question_count=Count("question", distinct=True),
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

    if organisation_id:
        voxpops = voxpops.filter(organisation=organisation_id)

    if voxpop_id:
        return voxpops.get(uuid=voxpop_id)

    return voxpops


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
