from uuid import UUID

from ninja import ModelSchema
from ninja import Router
from ninja import Schema

from django.conf import settings

from .models import Question
from .models import Voxpop
from .selectors import get_organisations
from .selectors import get_questions
from .selectors import get_voxpops
from .services import create_question
from .services import create_vote

import jwt

router = Router()


class QuestionIn(ModelSchema):
    class Config:
        model = Question
        model_fields = [
            "text",
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


@router.get("/login", response=Message)
def login(request, token: str = None):

    """ This endpoint will accept a JWT and
    overwrite the display_name, unique_name and
    optionally the admin session values. It is used
    to 'upgrade' an anonymous session to an identified
    session, which is required to participate in voxpops
    that do not allow anonymous participation. """

    if token:
        try:
            payload = jwt.decode(
                token,
                settings.SHARED_SECRET_JWT,
                algorithms=["HS256"]
            )
        except jwt.exceptions.InvalidSignatureError:
            return {"msg": "ERROR: Invalid signature"}
        except jwt.exceptions.DecodeError:
            return {"msg": "ERROR: Malformed JWT"}
        try:
            request.session["display_name"] = payload["display_name"]
            request.session["unique_name"] = payload["unique_name"]
            request.session["admin"] = payload["admin"]
        except KeyError:
            return {"msg": "Mandatory attribute(s) missing."}
        return {"msg": "Login successful."}
    return {"msg": "ERROR: Please provide a token."}


@router.post("{voxpop_id}/new_question", response=Message)
def new_question(request, voxpop_id: UUID, text: str):

    if not request.session.session_key:
        return {"msg": "No session found."}

    voxpop=get_voxpops(voxpop_id=voxpop_id)

    if (not voxpop.allow_anonymous) and (
        request.session.session_key == request.session["unique_name"]
    ):
        return {"msg": "Please sign in first."}

    question = create_question(
        text=text,
        display_name=request.session["display_name"],
        created_by=request.session["unique_name"],
        voxpop_id=voxpop_id,
    )

    return {"msg": "Question created with uuid: %s" % question.uuid}


@router.post("{voxpop_id}/questions/{question_id}/vote", response=Message)
def vote(request, voxpop_id: UUID, question_id: UUID):

    if not request.session.session_key:
        return {"msg": "No session found."}

    vote, created = create_vote(
        created_by=request.session.session_key,
        question_id=question_id,
    )

    return (
        {"msg": "Vote created with uuid: %s" % vote.uuid}
        if created
        else {"msg": "Vote already exists"}
    )


@router.get("/", response={200: list[VoxpopOut], 403: Message})
def voxpops(request):
    organisation = get_organisations(hostname=request.get_host())

    if organisation is None:
        return 403, {"msg": "Organisation not registered"}

    return 200, list(get_voxpops(organisation_id=organisation.uuid))


@router.get("/{voxpop_id}/questions", response=list[QuestionOut])
def questions(request, voxpop_id: UUID):

    # TODO: More Errorhandling here? Is this safe?

    if not request.session.session_key:
        request.session.create()
        request.session["display_name"] = "Anonymous"
        request.session["unique_name"] = request.session.session_key
        request.session["admin"] = False

    return list(get_questions(state=Question.State.APPROVED, voxpop_id=voxpop_id))


### Testing.
@router.get("/whoami")
def tell_me_who_I_am(request):
    if not request.session.session_key:
        return {"msg": "No session found."}
    return ({
        "display_name": request.session["display_name"],
        "unique_name": request.session["unique_name"],
        "admin": request.session["admin"],
        "anonymous": request.session["unique_name"] == request.session.session_key,
    })