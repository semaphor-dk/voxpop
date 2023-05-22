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
from .models import Question
from .selectors import current_organisation
from .selectors import get_questions
from .selectors import get_voxpops
from .services import create_question
from .utils import get_notify_channel_name


# Create your views here.
# from django.contrib.auth.decorators import login_required


def admin(request, voxpop_id: UUID = None):
    if request.session.get("admin") is True:
        if voxpop_id:
            context = {
                "voxpop": get_voxpops(voxpop_id=voxpop_id),
                "questions": {
                    "approved": get_questions(
                        voxpop_id=voxpop_id, state=Question.State.APPROVED
                    ),
                    "new": get_questions(voxpop_id=voxpop_id, state=Question.State.NEW),
                    "answered": get_questions(
                        voxpop_id=voxpop_id, state=Question.State.ANSWERED
                    ),
                    "discarded": get_questions(
                        voxpop_id=voxpop_id, state=Question.State.DISCARDED
                    ),
                },
            }

            return render(request, "voxpop/admin/voxpop.html", context)

        context = {
            "voxpops": get_voxpops(),
        }

        return render(request, "voxpop/admin/index.html", context)
    return render(request, "voxpop/admin/auth_error.html")


def index(request):
    org = current_organisation(request)
    context = {}
    if org:
        context["current_organisation"] = org
        voxpop = get_voxpops(organisation_id=org.uuid).last()
        if voxpop:
            context["voxpop_id"] = voxpop.uuid
        else:
            context["voxpop_id"] = ""
    else:
        context["current_organisation"] = None
        context["voxpop_id"] = ""
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
    voxpop = get_voxpops(voxpop_id=voxpop_id)
    form = QuestionForm
    if request.method == "POST":
        form = QuestionForm(request.POST)
        if form.is_valid():
            formdata = form.save(commit=False)
            create_question(
                formdata.text,
                request.session.session_key,
                "anonymous" if voxpop.allow_anonymous else "shouldBeKnown",
                voxpop_id,
            )
            if voxpop.is_moderated:
                messages.info(request, "Dit spørgsmål er nu sendt til godkendelse.")
            return redirect("voxpop:index")
        else:
            return HttpResponse("Ukendt fejl, prøv venligst igen.")

    return render(request, "voxpop/question.html", {"form": form})


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
    async with aconnection.cursor() as acursor:
        await acursor.execute(f"LISTEN {channel_name}")
        gen = aconnection.notifies()
        async for notify in gen:
            yield f"{notify.payload}\n\n"


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
            "Cache-Control": "No-Cache",
        },
    )
