from django.contrib import messages
from django.http import HttpRequest
from django.http import HttpResponse
from django.shortcuts import Http404
from django.shortcuts import redirect
from django.shortcuts import render

from .forms import QuestionForm
from .models import Question
from .selectors import get_questions
from .selectors import get_voxpops


# Create your views here.
# from django.contrib.auth.decorators import login_required


def index(request):
    approved_question_list = Question.objects.filter(state="approved")
    context = {
        "approved_question_list": approved_question_list,
    }
    return render(request, "voxpop/index.html", context)


def detail(request, question_id):
    try:
        question = get_questions(question_id=question_id)
    except Question.DoesNotExist:
        raise Http404("Question does not exist")
    context = {
        "question": question,
        "id": question.id,
    }
    return render(request, "voxpop/detail.html", context)


def new_question(request: HttpRequest, voxpop_id: int) -> HttpResponse:
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


def vote(request, question_id):
    question = Question.objects.get(pk=question_id)
    question.upvote()
    question.save()
    context = {
        "question": question.text,
    }
    return render(request, "voxpop/vote.html", context)
