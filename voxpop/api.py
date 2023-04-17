from ninja import Router

from .models import Question


router = Router()


@router.get("/questions")
def get_all(request, only_approved: bool = "false"):
    approved_question_list = (
        Question.objects.filter(approved=True).values()
        if only_approved
        else Question.objects.values()
    )
    all_questions = []
    for quest in approved_question_list:
        all_questions.append(quest)
    return all_questions
