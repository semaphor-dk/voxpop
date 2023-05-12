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
from .utils import get_notify_channel_name


# Create your views here.
# from django.contrib.auth.decorators import login_required


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
            question = form.save(commit=False)
            question.voxpop = voxpop
            question.save()
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
    aconnection = await psycopg.AsyncConnection.connect(
        **connection.get_connection_params(),
        autocommit=True,
    )
    channel_name = get_notify_channel_name(voxpop_id=voxpop_id)
    async with aconnection:
        async with aconnection.cursor() as acursor:
            await acursor.execute(f"LISTEN {channel_name}")
            gen = aconnection.notifies()
            async for notify in gen:
                yield f"data: {notify.payload}\n\n"


async def stream_questions_view(
    request: HttpRequest,
    voxpop_id: UUID,
) -> StreamingHttpResponse:
    return StreamingHttpResponse(
        streaming_content=stream_questions(voxpop_id=voxpop_id),
        content_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Transfer-Encoding": "chunked",
        },
    )
