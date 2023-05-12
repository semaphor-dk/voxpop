from __future__ import annotations  # For Python3.9 users.

from uuid import UUID
from django.utils import timezone

from django.db.models import (
    Count, Case, When, BooleanField, Q, QuerySet
)

from voxpop.models import (
    Question, Vote, Voxpop, Organisation
)


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
    
    current_time = timezone.now()
    voxpops = Voxpop.objects.all().annotate(
        question_count=Count("question", distinct=True),
        is_active=Case(
            When(Q(starts_at__lte=current_time) & Q(expires_at__gte=current_time), then=True),
            default=False,
            output_field=BooleanField(),
        )
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
