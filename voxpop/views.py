from collections.abc import AsyncGenerator
from uuid import UUID

import psycopg
import jwt

from django.contrib import messages
from django.db import connection
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import StreamingHttpResponse
from django.shortcuts import Http404
from django.shortcuts import redirect
from django.shortcuts import render
from django.conf import settings

from .forms import QuestionForm
from .forms import VoxpopForm
from .models import Question
from .selectors import current_organisation
from .selectors import get_messages
from .selectors import get_questions
from .selectors import get_voxpops
from .selectors import get_voxpop
from .services import create_question
from .services import create_voxpop
from .utils import get_notify_channel_name

from django.utils.translation import gettext_lazy as _


def is_admin(request):
    return request.session.get("admin")


def admin_index(request):
    organisation = current_organisation(request)
    if is_admin(request):
        if organisation:
            context = {
                "voxpops": get_voxpops(organisation),
                "organisation": organisation
            }
        else:
            messages.warning(request, "Der findes ingen organisation til dette hostnavn!")
            context = {"organisation": organisation}
        return render(request, "voxpop/admin/index.html", context)

    # TODO: Handle non-admin user request to "/admin"?
    #return render(request, "voxpop/admin/auth_error.html")

    token = request.GET.get('token', False)
    if token:
        try:
            payload = jwt.decode(token,
                                 settings.SHARED_SECRET_JWT,
                                 algorithms=["HS256"])

        except jwt.exceptions.InvalidSignatureError:
            msg=_("invalid signature")
            return render(request,
                          "voxpop/admin/auth_error.html",
                          {"error": msg})

        except jwt.exceptions.DecodeError:
            msg=_("jwt decode error")
            return render(request,
                          "voxpop/admin/auth_error.html",
                          {"error": msg})
        try:
            request.session["display_name"] = payload["display_name"]
            request.session["unique_name"] = payload["unique_name"]
            request.session["admin"] = payload["admin"]
        except KeyError:
            return {"msg": "Mandatory attribute(s) missing."}
        return redirect("/admin")

    idp_url = organisation.idp + "?url=https://" + request.get_host()
    return redirect(idp_url)

def admin_voxpop(request, voxpop_id: UUID = None):
    if is_admin(request):
        if voxpop_id:
            voxpop = get_voxpop(voxpop_id=voxpop_id)
            context = {
                "voxpop": voxpop,
                "questions": {
                    "new": get_questions(
                        voxpop=voxpop,
                        state=Question.State.NEW),
                    "approved": get_questions(
                        voxpop=voxpop,
                        state=Question.State.APPROVED),
                    "answered": get_questions(
                        voxpop=voxpop,
                        state=Question.State.ANSWERED),
                    "discarded": get_questions(
                        voxpop=voxpop,
                        state=Question.State.DISCARDED),
                },
            }
            return render(request, "voxpop/admin/voxpop.html", context)
    return render(request, "voxpop/admin/auth_error.html")


def admin_question_set_state(request, voxpop_id, question_id):
    if is_admin(request):
        new_state = request.GET.get('state', None)
        question = Question.objects.get(uuid=question_id)
        question.state = new_state
        question.save()
        return HttpResponse(status=204)


def new_voxpop(request):
    if is_admin(request):
        if request.method == "GET":
            context = {
                "form": VoxpopForm()
            }
            return render(request, "voxpop/admin/new_voxpop.html", context)
        if request.method == "POST":
            form = VoxpopForm(request.POST)
            if form.is_valid():
                formdata = form.save(commit=False)
                voxpop = create_voxpop(
                    formdata.title,
                    formdata.description,
                    request.session["unique_name"],
                    formdata.starts_at,
                    formdata.expires_at,
                    formdata.is_moderated,
                    formdata.allow_anonymous,
                    current_organisation(request),
                )
                return redirect("/admin")
            else:
                print("Form invalid")
            return redirect("/admin/voxpops/new")
    return render(request, "voxpop/admin/auth_error.html")

def edit_voxpop(request, voxpop_id: UUID = None):
    if is_admin(request):
        voxpop = get_voxpop(voxpop_id)
        if request.method == "GET":
            context = {
                       "voxpop": voxpop,
                       "form": VoxpopForm(instance=voxpop)
                       }
            return render(request, "voxpop/admin/edit_voxpop.html", context)

        if request.method == "POST":
            form = VoxpopForm(request.POST, instance=voxpop)
            form.save(commit=True)
            return redirect("/admin")

def index(request):
    org = current_organisation(request)
    context = {}
    context["current_organisation"] = org
    context["voxpop_id"] = ""
    context["allow_anonymous"] = False
    if org:
        voxpop = get_voxpops(org).filter(is_active=True).order_by("starts_at").last()
        if voxpop:
            context["voxpop"] = voxpop
    return render(request, "voxpop/index.html", context)


def detail(request, question_id: UUID):
    try:
        question = get_questions(question_id=question_id)
    except Question.DoesNotExist:
        raise Http404("Question does not exist")
    context = {
        "question": question,
        "id": question.uuid,
    }
    return render(request, "voxpop/detail.html", context)


def new_question(request: HttpRequest, voxpop_id: UUID) -> HttpResponse:
    voxpop = get_voxpop(voxpop_id=voxpop_id)
    form = QuestionForm
    if request.method == "POST":
        form = QuestionForm(request.POST)
        if form.is_valid():
            formdata = form.save(commit=False)
            create_question(
                formdata.text,
                request.session.session_key,
                formdata.display_name,
                voxpop_id,
            )
            if voxpop.is_moderated:
                messages.info(request, "Dit spørgsmål er nu sendt til godkendelse.")
            return redirect("voxpop:index")
        else:
            return HttpResponse("Ukendt fejl, prøv venligst igen.")

    return render(request, "voxpop/question.html", {"form": form, "allow_anonymous": voxpop.allow_anonymous})


async def __stream_questions(*, channel_prefix: str,voxpop_id: UUID, last_event_id: int) -> AsyncGenerator[str, None]:
    aconnection = await psycopg.AsyncConnection.connect(
        **connection.get_connection_params(),
        autocommit=True,
    )
    channel_name = get_notify_channel_name(channel_prefix=channel_prefix, voxpop_id=voxpop_id)
    if last_event_id > 0:  # Reconnect request
        print("Reconnecting from id " + str(last_event_id))
        missed_messages = await get_messages(channel_name, last_event_id)
        if len(missed_messages) == 0:  # Send a dummy response to activate the stream.
            yield "event: ping\ndata: Pong\n\n"
        else:
            yield "".join([str(m) for m in missed_messages])
    else:  # Send a dummy response to activate the stream.
        print("New SSE connection.")
        yield "event: ping\ndata: Pong\n\n"

    try:
        async with aconnection.cursor() as acursor:
            await acursor.execute(f"LISTEN {channel_name}")
            gen = aconnection.notifies()
            async for notify in gen:
                yield notify.payload
    except Exception as e:
        print(e.message)
    finally:
        print("Closing database connection!")
        await aconnection.close()


async def questions_stream_view(
    request: HttpRequest,
    channel_prefix: str,
    voxpop_id: UUID,
) -> StreamingHttpResponse:
    last_event_id = int(request.headers.get("Last-Event-Id", 0))
    return StreamingHttpResponse(
        content_type="text/event-stream",
        headers={
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Credentials": "true",
            "Cache-Control": "No-Cache"
        },
        streaming_content=__stream_questions(channel_prefix=channel_prefix, voxpop_id=voxpop_id, last_event_id=last_event_id),
    )
