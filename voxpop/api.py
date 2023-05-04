from uuid import UUID

from django.http import Http404
from django.core.exceptions import BadRequest
from ninja import ModelSchema
from ninja import Router
from ninja import Schema

from .models import Question
from .models import Vote
from .models import Voxpop
from .selectors import get_questions
from .selectors import get_votes
from .selectors import get_voxpops
from .services import create_question
from .services import create_vote


router = Router()


class QuestionIn(ModelSchema):
    class Config:
        model = Question
        model_fields = [
            "text",
            "display_name",
        ]


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


class Message(Schema):
    msg: str


@router.post("{voxpop_id}/new_question", response=Message)
def new_question(request, voxpop_id: UUID, payload: QuestionIn):

    question = create_question(
        **payload.dict(),
        created_by=session_key,
        voxpop_id=voxpop_id,
    )
    
    return {"msg": "Question created with uuid: %s" % question.uuid}


@router.post("{voxpop_id}/questions/{question_id}/vote", response=Message)
def vote(request, voxpop_id: UUID, question_id: UUID):
 
    vote, created = create_vote(
        created_by=session_key,
        question_id=question_id,
        )

    if created:
        return {"msg": "Vote created with uuid: %s" % vote.uuid}
    return {"msg": "Vote already exists"}


@router.get("/", response=list[VoxpopOut])
def voxpops(request):
    return list(get_voxpops())


@router.get("/{voxpop_id}/questions", response=list[QuestionOut])
def questions(request, voxpop_id: UUID):
    
    if not request.session.session_key: 
        request.session.create()

    return list(get_questions(state=Question.State.APPROVED, voxpop_id=voxpop_id))
