from django.db.models import Count
from django.db.models import QuerySet

from voxpop.models import Question
from voxpop.models import Voxpop


def get_questions(
    question_id: int | None = None,
    state: Question.State | None = None,
) -> "QuerySet[Question] | Question":
    questions = Question.objects.all().annotate(
        vote_count=Count("votes", distinct=True),
    )

    if question_id:
        return questions.get(id=question_id)

    if state:
        questions = questions.filter(state=state)

    return questions


def get_voxpops(voxpop_id: int | None = None) -> "QuerySet[Voxpop] | Voxpop":
    voxpops = Voxpop.objects.all()

    if voxpop_id:
        return voxpops.get(id=voxpop_id)

    return voxpops
