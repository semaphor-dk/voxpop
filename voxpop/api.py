from ninja import Router, Schema

from .models import Question, Vote
import json

router = Router()


@router.get("/questions")
def get_questions(request):
    return list(q.as_dict() for q in Question.objects.filter(state="approved").all())
