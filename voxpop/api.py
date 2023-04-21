from datetime import datetime

from ninja import Router
from ninja import Schema

from .models import Question
from .selectors import get_questions
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
    starts_at: datetime
    expires_at: datetime
    question_count: int
    is_moderated: bool
    allow_anonymous: bool

@router.get("/questions", response=list[QuestionSchema])
def questions(request):
    return list(get_questions(state=Question.State.APPROVED))

@router.get("/voxpops", response=list[VoxpopSchema])
def voxpops(request):
    return(list(get_voxpops()))