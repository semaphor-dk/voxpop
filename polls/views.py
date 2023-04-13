from django.shortcuts import render, redirect

# Create your views here.
from django.http import HttpResponse
from django.shortcuts import Http404
#from django.contrib.auth.decorators import login_required

from .models import Question
from .forms import QuestionForm
import json


def index(request):
    approved_question_list = Question.objects.filter(approved=True).order_by('-vote_count')
    context = {
        'approved_question_list': approved_question_list,
    }
    return render(request, 'polls/index.html', context)


def detail(request, question_id):
    try:
        question = Question.objects.get(pk=question_id)
    except Question.DoesNotExist:
        raise Http404("Question does not exist")
    context = {
        'question': question.question_text,
        'votes': question.vote_count,
        'id': question.id,
    }
    return render(request, 'polls/detail.html', context)


def new_question(request):
    if request.method == "GET":
        form = QuestionForm
        return render(request, 'polls/question.html', {'form': form})
    if request.method == "POST":
        form = QuestionForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']
            newq = Question(question_text=text)
            newq.save()
            del newq
        else:
            return HttpResponse("Ukendt fejl, prøv venligst igen.")
            
        approved_question_list = Question.objects.filter(approved=True).order_by('-vote_count')
        return redirect("/polls/")


def vote(request, question_id):
    question = Question.objects.get(pk=question_id)
    question.upvote()
    question.save()
    context = {
        'question': question.question_text,
    }
    return render(request, 'polls/vote.html', context)
