from uuid import UUID

from voxpop.models import Question
from voxpop.models import Vote
from voxpop.selectors import get_voxpops


def create_question(
    text: str,
    created_by: str,
    display_name: str,
    voxpop_id: UUID,
) -> Question:
    voxpop = get_voxpops(voxpop_id=voxpop_id)

    question = Question.objects.create(
        text=text,
        created_by=created_by,
        display_name=display_name,
        voxpop=voxpop,
        state=Question.State.NEW if voxpop.is_moderated else Question.State.APPROVED,
    )

    return question


def create_vote(
    created_by: str,
    question_id: UUID,
) -> (Vote, bool):
    vote, created = Vote.objects.get_or_create(
        created_by=created_by,
        question_id=question_id,
    )

    return vote, created
