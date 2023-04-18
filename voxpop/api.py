from ninja import Router, Schema

from .models import Question, Vote
import json

router = Router()

@router.get("/questions")
def get_questions(request, only_approved: bool = "false"):
    return (
        list(q.as_dict() for q in Question.objects.filter(approved=True).all()) 
        if only_approved else 
        list(q.as_dict() for q in Question.objects.all())
    )


class VoteSchema(Schema):
    name: str
    question_id: int

class Error(Schema):
    msg: str

"""
@router.post("/vote", response={200: VoteSchema, 405: Error})
def vote_on_question(request, data: VoteSchema):
    if Vote.objects.all().filter(vote_by=data.name).first() == None:
        v = Vote(
            vote_by=data.name, 
            question=Question.objects.get(pk=data.question_id)
        )
        v.save()
        return 200, {"message": "Success"}
    else: return 405, {"message": "Already posted on question"}"""