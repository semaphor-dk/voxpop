from django.http import HttpResponse
from django.shortcuts import Http404
from django.shortcuts import redirect
from django.shortcuts import render

from .forms import QuestionForm
from .models import Question

# Create your views here.
# from django.contrib.auth.decorators import login_required


def index(request):
    approved_question_list = Question.objects.filter(approved=True)
    context = {
        "approved_question_list": approved_question_list,
    }
    return render(request, "voxpop/index.html", context)


def detail(request, question_id):
    try:
        question = Question.objects.get(pk=question_id)
    except Question.DoesNotExist:
        raise Http404("Question does not exist")
    context = {
        "question": question.text,
        "id": question.id,
        "votes": question.get_votes(),
    }
    return render(request, "voxpop/detail.html", context)


def new_question(request):
    if request.method == "GET":
        form = QuestionForm
        return render(request, "voxpop/question.html", {"form": form})
    if request.method == "POST":
        form = QuestionForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data["text"]
            newq = Question(text=text)
            newq.save()
        else:
            return HttpResponse("Ukendt fejl, prøv venligst igen.")

        Question.objects.filter(approved=True)
        return redirect("voxpop:index")


def vote(request, question_id):
    question = Question.objects.get(pk=question_id)
    question.upvote()
    question.save()
    context = {
        "question": question.text,
    }
    return render(request, "voxpop/vote.html", context)
