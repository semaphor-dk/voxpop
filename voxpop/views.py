from collections.abc import AsyncGenerator
from uuid import UUID

import psycopg
from django.contrib import messages
from django.db import connection
from django.http import HttpRequest
from django.http import HttpResponse
from django.http import StreamingHttpResponse
from django.shortcuts import Http404
from django.shortcuts import redirect
from django.shortcuts import render

from .forms import QuestionForm
from .forms import VoxpopForm
from .models import Question
from .selectors import current_organisation
from .selectors import get_questions
from .selectors import get_voxpops
from .selectors import get_voxpop
from .services import create_question
from .services import create_voxpop
from .utils import get_notify_channel_name


# Create your views here.
# from django.contrib.auth.decorators import login_required

def is_admin(request):
    return True
    return request.session.get("admin")


def admin_index(request):
    if is_admin(request):
        organisation = current_organisation(request)
        if organisation:
            context = {
                "voxpops": get_voxpops(organisation),
                "organisation": organisation
            }
        else:
            messages.warning(request, "Der findes ingen organisation til dette hostnavn!")
            context = {"organisation": organisation}
        return render(request, "voxpop/admin/index.html", context)
    return render(request, "voxpop/admin/auth_error.html")


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
                    "discarded": get_questions(
                        voxpop=voxpop,
                        state=Question.State.DISCARDED),
                    "answered": get_questions(
                        voxpop=voxpop,
                        state=Question.State.ANSWERED),
                },
            }
            return render(request, "voxpop/admin/voxpop.html", context)
    return render(request, "voxpop/admin/auth_error.html")


def admin_question_set_state(request, voxpop_id, question_id):
    if is_admin(request):
        new_state = request.GET.get('state', None)
        if new_state:
            print(question_id)
            print(new_state)
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


def vote(request, question_id: UUID):
    question = Question.objects.get(pk=question_id)
    question.upvote()
    question.save()
    context = {
        "question": question.text,
    }
    return render(request, "voxpop/vote.html", context)


async def stream_questions(*, voxpop_id: UUID) -> AsyncGenerator[str, None]:
    yield "data: Ping\n\n"
    aconnection = await psycopg.AsyncConnection.connect(
        **connection.get_connection_params(),
        autocommit=True,
    )
    channel_name = get_notify_channel_name(voxpop_id=voxpop_id)
    try:
        async with aconnection.cursor() as acursor:
            await acursor.execute(f"LISTEN {channel_name}")
            gen = aconnection.notifies()
            async for notify in gen:
                yield f"{notify.payload}\n\n"
    except Exception as e:
        print(e.message)
    finally:
        aconnection.close()


async def stream_questions_view(
    request: HttpRequest,
    voxpop_id: UUID,
) -> StreamingHttpResponse:
    return StreamingHttpResponse(
        streaming_content=stream_questions(voxpop_id=voxpop_id),
        content_type="text/event-stream",
        headers={
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Credentials": "true",
            "Cache-Control": "No-Cache"
        },
    )
