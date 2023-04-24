from __future__ import annotations  # For Python3.9 users.

from django.db.models import Count
from django.db.models import QuerySet

from voxpop.models import Question
from voxpop.models import Vote
from voxpop.models import Voxpop


def get_questions(
    question_id: int | None = None,
    state: Question.State | None = None,
) -> QuerySet[Question] | Question:
    questions = Question.objects.all().annotate(
        vote_count=Count("votes", distinct=True),
    )

    if question_id:
        return questions.get(id=question_id)

    if state:
        questions = questions.filter(state=state)

    return questions


# TODO: Annotate "is_active" somehow...
def get_voxpops(voxpop_id: int | None = None) -> QuerySet[Voxpop] | Voxpop:
    voxpops = Voxpop.objects.all().annotate(
        question_count=Count("question", distinct=True),
    )

    if voxpop_id:
        return voxpops.get(id=voxpop_id)

    return voxpops


def get_votes(vote_id: int | None = None) -> QuerySet[Vote] | Vote:
    votes = Vote.objects.all()

    if vote_id:
        return votes.get(id=vote_id)

    return votes
