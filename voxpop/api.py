from django.http import Http404
from ninja import ModelSchema
from ninja import Router
from ninja import Schema
from uuid import UUID

from .models import Question
from .models import Vote
from .models import Voxpop
from .selectors import get_questions
from .selectors import get_votes
from .selectors import get_voxpops

router = Router()


class QuestionOut(ModelSchema):
    class Config:
        model = Question
        model_fields = [
            "uuid",
            "voxpop",
            "text",
            "created_at",
            "created_by",
            "display_name",
            "state",
        ]

    vote_count: int


class QuestionIn(ModelSchema):
    class Config:
        model = Question
        model_fields = [
            "text",
            "created_by",
            "display_name",
        ]


class VoxpopOut(ModelSchema):
    class Config:
        model = Voxpop
        model_fields = [
            "uuid",
            "title",
            "description",
            "created_by",
            "starts_at",
            "expires_at",
            "is_moderated",
            "allow_anonymous",
        ]

    question_count: int


class VoteOut(ModelSchema):
    class Config:
        model = Vote
        model_fields = [
            "uuid",
            "question",
            "created_by",
        ]

class Message(Schema):
    msg: str


@router.post("{voxpop_id}/new_question", response=Message)
def new_question(request, voxpop_id: UUID, payload: QuestionIn):
    
    try: voxpop = get_voxpops(voxpop_id=voxpop_id)
    except Exception as err: return {"msg": "%s" %err}

    question = Question.objects.create(
        **payload.dict(), 
        voxpop=voxpop
    )  

    return {"msg": "Question created with uuid: %s" %question.uuid}


@router.get("/", response=list[VoxpopOut])
def voxpops(request):
    return list(get_voxpops())


@router.get("/{voxpop_id}", response=VoxpopOut)
def voxpop(request, voxpop_id: UUID):
    return get_voxpops(voxpop_id=voxpop_id)


@router.get(
    "/{voxpop_id}/questions", 
    response=list[QuestionOut]
)
def questions(request, voxpop_id: UUID):
    return list(get_questions(state=Question.State.APPROVED, voxpop_id=voxpop_id))


@router.get(
    "/{voxpop_id}/questions/{question_id}", 
    response={200: QuestionOut}
)
def question(request, voxpop_id: UUID, question_id: UUID):
    if _question := get_questions(
        question_id=question_id,
        voxpop_id=voxpop_id,
        state=Question.State.APPROVED,
    ):
        return 200, _question
    raise Http404


@router.get(
    "/{voxpop_id}/questions/{question_id}/votes",
    response={200: list[VoteOut]},
)
def votes(request, voxpop_id: UUID, question_id: UUID):
    return list(get_votes(question_id=question_id, voxpop_id=voxpop_id))


@router.get(
    "/{voxpop_id}/questions/{question_id}/votes/{vote_id}",
    response={200: VoteOut},
)
def vote(request, voxpop_id: UUID, question_id: UUID, vote_id: UUID):
    if _vote := get_votes(
        vote_id=vote_id,
        question_id=question_id,
        voxpop_id=voxpop_id,
    ):
        return 200, _vote

    raise Http404
