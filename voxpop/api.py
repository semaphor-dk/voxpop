from datetime import datetime

from ninja import Router
from ninja import Schema

from .models import Question
from .selectors import get_questions
from .selectors import get_votes
from .selectors import get_voxpops

router = Router()


class QuestionSchema(Schema):
    id: int
    voxpop_id: int
    text: str
    created_at: datetime
    created_by: str
    state: str
    vote_count: int


class VoxpopSchema(Schema):
    id: int
    organisation_id: int
    title: str
    description: str
    created_by: str
    starts_at: datetime
    expires_at: datetime
    question_count: int
    is_moderated: bool
    allow_anonymous: bool


class VoteSchema(Schema):
    id: int
    question_id: int
    created_by: str

class Error(Schema):
    msg: str


@router.get("/", response=list[VoxpopSchema])
def voxpops(request):
    return list(get_voxpops())


@router.get("/{voxpop_id}", response=VoxpopSchema)
def voxpop(request, voxpop_id: int):
    return get_voxpops(voxpop_id=voxpop_id)


@router.get("/{voxpop_id}/questions", response=list[QuestionSchema])
def questions(request, voxpop_id: int):
    # TODO: Make sure voxpop exists.
    return list(get_questions(state=Question.State.APPROVED).filter(voxpop_id=voxpop_id))


@router.get("/{voxpop_id}/questions/{question_id}", response={200: QuestionSchema, 500: Error})
def question(request, voxpop_id: int, question_id: int):
    if get_questions(question_id=question_id).voxpop_id == voxpop_id:
        return 200, get_questions(state=Question.State.APPROVED, question_id=question_id)
    return 500, {"msg": "Container error"}


@router.get("/{voxpop_id}/questions/{question_id}/votes", response={200: list[VoteSchema], 500: Error})
def votes(request, voxpop_id: int, question_id: int):
    if get_questions(question_id=question_id).voxpop_id == voxpop_id:
        return list(get_votes().filter(question_id=question_id))
    return 500, {"msg": "Container error"}


@router.get("/{voxpop_id}/questions/{question_id}/votes/{vote_id}", response={200: VoteSchema, 500: Error})
def vote(request, voxpop_id: int, question_id: int, vote_id: int):
    if (get_questions(question_id=question_id).voxpop_id == voxpop_id and 
        get_votes(vote_id=vote_id).question_id == question_id):
        return get_votes(vote_id=vote_id)
    return 500, {"msg": "Container error"}