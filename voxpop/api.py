from datetime import datetime

from ninja import Router
from ninja import Schema

from .models import Question
from .selectors import get_questions

router = Router()


class QuestionSchema(Schema):
    id: int
    voxpop_id: int
    text: str
    created_at: datetime
    created_by: str
    state: str
    vote_count: int


@router.get("/questions", response=list[QuestionSchema])
def questions(request):
    return list(get_questions(state=Question.State.APPROVED))
