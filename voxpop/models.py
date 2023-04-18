import datetime

from django.db import models
from django.utils import timezone

# TODO: What is this for?
datetime.timedelta(days=1)

"""
class Organisation(models.Model):
    name = models.CharField(max_length=200)
    
    def __str__(self):
        return self.name

class Topic(models.Model):
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=500, blank=True)
    created = models.DateTimeField("date created", default=timezone.now()
    ...
"""

class Question(models.Model):
    text = models.CharField(max_length=200)
    created = models.DateTimeField("date published", default=timezone.now)
    approved = models.BooleanField("approve", default=False)

    def approve(self):
        self.approved = True

    def get_votes(self):
        return len(Vote.objects.values().filter(question_id=self.id))

    def as_dict(self):
        return ({
            "id": self.id,
            "text": self.text,
            "created": self.created,
            "approved": self.approved,
            "vote_count": self.get_votes(),
        })

    def __str__(self):
        return f'[{self.created.time()}]: "{self.text}"'

class Vote(models.Model):

    vote_by = models.CharField(max_length=200)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.vote_by} -> "{self.question.text}"'
