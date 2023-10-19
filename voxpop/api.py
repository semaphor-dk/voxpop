import unicodedata
from uuid import UUID

import jwt
from django.conf import settings
from ninja import ModelSchema
from ninja import Router
from ninja import Schema
from ninja_extra import throttle
from ninja_extra.throttling import UserRateThrottle

from .models import Question
from .models import Voxpop
from .selectors import current_organisation
from .selectors import get_questions
from .selectors import get_voxpop
from .selectors import get_voxpops
from .services import create_question
from .services import create_vote

router = Router()


def safe_string(s: str) -> bool:
    return all([unicodedata.category(ch) in ["Ll", "Zs", "Lu", "Po"] for ch in s])


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


class QuestionsOut(Schema):
    approved: list[QuestionOut]
    answered: list[QuestionOut]


class QuestionsOutAdmin(Schema):
    new: list[QuestionOut]
    approved: list[QuestionOut]
    answered: list[QuestionOut]
    discarded: list[QuestionOut]


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


class LoginSchema(Schema):
    token: str


class QuestionRate(UserRateThrottle):
    rate = "3/min"
    scope = "minutes"


class VoteRate(UserRateThrottle):
    rate = "10/min"
    scope = "minutes"


@router.post(
    "{voxpop_id}/questions/new",
    response=Message,
)
@throttle(QuestionRate)
def new_question(request, voxpop_id: UUID, data: QuestionIn):
    if not request.session.session_key:
        return {"msg": "No session found."}
    voxpop = get_voxpop(voxpop_id)
    
    # Sanitize user-input.
    if safe_string(data.display_name) is False or safe_string(data.text) is False:
        return {"msg": "Message contains inappropriate symbols"}

    if voxpop.allow_anonymous:
        question = create_question(
            text=data.text,
            display_name=request.session.get(
                "display_name",
                data.display_name if data.display_name else "",
            ),
            created_by=request.session.get(
                "unique_name",
                request.session.session_key,
            ),
            voxpop_id=voxpop_id,
        )
    else:
        if not request.session.get("display_name", False):
            return {"msg": "Please sign in first."}
        question = create_question(
            text=data.text,
            display_name=request.session["display_name"],
            created_by=request.session["unique_name"],
            voxpop_id=voxpop_id,
        )
    return {"msg": "Question created with uuid: %s" % question.uuid}


@throttle(VoteRate)
@router.post(
    "{voxpop_id}/questions/{question_id}/vote",
    response=Message,
)
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


@router.get(
    "/",
    response={
        200: list[VoxpopOut],
        403: Message,
    },
)
def voxpops(request):
    organisation = current_organisation(request)
    if organisation is None:
        return 403, {"msg": "Organisation not registered"}
    return 200, list(get_voxpops(organisation))


@router.get(
    "/{voxpop_id}/questions",
    response=QuestionsOut,
)
def questions(request, voxpop_id: UUID):
    if not request.session.session_key:
        request.session.create()
    voxpop = get_voxpop(voxpop_id)
    approved = list(
        get_questions(
            state=Question.State.APPROVED,
            voxpop=voxpop,
        ),
    )
    answered = list(
        get_questions(
            state=Question.State.ANSWERED,
            voxpop=voxpop,
        ),
    )

    return {"approved": approved, "answered": answered}


@router.get(
    "/{voxpop_id}/all_questions",
    response={
        200: QuestionsOutAdmin,
        401: Message,
    },
)
def all_questions(request, voxpop_id: UUID):
    if request.session.get("admin", False):
        voxpop = get_voxpop(voxpop_id)
        new = list(
            get_questions(
                state=Question.State.NEW,
                voxpop=voxpop,
            ),
        )
        approved = list(
            get_questions(
                state=Question.State.APPROVED,
                voxpop=voxpop,
            ),
        )
        answered = list(
            get_questions(
                state=Question.State.ANSWERED,
                voxpop=voxpop,
            ),
        )
        discarded = list(
            get_questions(
                state=Question.State.DISCARDED,
                voxpop=voxpop,
            ),
        )
        return {
            "new": new,
            "approved": approved,
            "answered": answered,
            "discarded": discarded,
        }
    return 401, {"msg": "Unauthorized"}


@router.post("/login", response=Message)
def login(request, data: LoginSchema):
    """This endpoint will accept a JWT and
    overwrite the display_name, unique_name and
    optionally the admin session values. It is used
    to 'upgrade' an anonymous session to an identified
    session, which is required to participate in voxpops
    that do not allow anonymous participation."""

    if data.token:
        try:
            payload = jwt.decode(
                data.token,
                settings.SHARED_SECRET_JWT,
                algorithms=["HS256"],
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


@router.get("/whoami")
def tell_me_who_I_am(request):
    if not request.session.session_key:
        request.session.create()

    info = {k: v for k, v in request.session.items()}
    info["sessionid"] = request.session.session_key
    return info


@router.get("/logout")
def logout(request):
    request.session.clear()
    return {"msg": "Logged out"}


@router.get(
    "/{voxpop_id}",
    response={
        200: VoxpopOut,
        403: Message,
    },
)
def voxpop_detail(request, voxpop_id: UUID):
    """Need to be placed after /login /whoami and /logout
    as they occupy the same location but need to matched in a
    certain order."""

    voxpop = get_voxpop(voxpop_id)
    print(voxpop)
    if voxpop is not None:
        return 200, voxpop
    else:
        return 403, {"msg": "Voxpop not found"}
