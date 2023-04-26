from django.http import Http404
from ninja import ModelSchema
from ninja import Router
from ninja import Schema

from .models import Question
from .models import Vote
from .models import Voxpop
from .selectors import get_questions
from .selectors import get_votes
from .selectors import get_voxpops

router = Router()


class QuestionSchema(ModelSchema):
    class Config:
        model = Question
        model_fields = [
            "id",
            "voxpop",
            "text",
            "created_at",
            "created_by",
            "state",
        ]

    vote_count: int


class VoxpopSchema(ModelSchema):
    class Config:
        model = Voxpop
        model_fields = [
            "id",
            "organisation",
            "title",
            "description",
            "created_by",
            "starts_at",
            "expires_at",
            "is_moderated",
            "allow_anonymous",
        ]

    question_count: int


class VoteSchema(ModelSchema):
    class Config:
        model = Vote
        model_fields = [
            "id",
            "question",
            "created_by",
        ]


@router.get("/", response=list[VoxpopSchema])
def voxpops(request):
    return list(get_voxpops())


@router.get("/{voxpop_id}", response=VoxpopSchema)
def voxpop(request, voxpop_id: int):
    return get_voxpops(voxpop_id=voxpop_id)


@router.get("/{voxpop_id}/questions", response=list[QuestionSchema])
def questions(request, voxpop_id: int):
    return list(get_questions(state=Question.State.APPROVED, voxpop_id=voxpop_id))


@router.get("/{voxpop_id}/questions/{question_id}", response={200: QuestionSchema})
def question(request, voxpop_id: int, question_id: int):
    if _question := get_questions(
        question_id=question_id,
        voxpop_id=voxpop_id,
        state=Question.State.APPROVED,
    ):
        return 200, _question
    raise Http404


@router.get(
    "/{voxpop_id}/questions/{question_id}/votes",
    response={200: list[VoteSchema]},
)
def votes(request, voxpop_id: int, question_id: int):
    return list(get_votes(question_id=question_id, voxpop_id=voxpop_id))


@router.get(
    "/{voxpop_id}/questions/{question_id}/votes/{vote_id}",
    response={200: VoteSchema},
)
def vote(request, voxpop_id: int, question_id: int, vote_id: int):
    if _vote := get_votes(
        vote_id=vote_id,
        question_id=question_id,
        voxpop_id=voxpop_id,
    ):
        return 200, _vote

    raise Http404
