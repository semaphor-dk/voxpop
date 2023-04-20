import datetime

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class Organisation(models.Model):

    # Work in progress.
    name = models.CharField(max_length=200)
    hostname = models.CharField(max_length=200)
    idp = models.CharField(max_length=200)
    admin_group = models.CharField(max_length=200)
    
    def __str__(self):
        return self.name

class Voxpop(models.Model):
    
    title = models.CharField(max_length=50) # evt. topic
    description = models.TextField(blank=True)
    created_at = models.DateTimeField("Date created", default=timezone.now)
    created_by = models.CharField(max_length=50)
    starts_at = models.DateTimeField("Starttime")
    expires_at = models.DateTimeField("Endtime")
    is_moderated = models.BooleanField(default=True)
    allow_anonymous = models.BooleanField(default=False)
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE) 

    # Use SQL.
    # Pseudocode.
    #def is_active(self) -> bool:
    #    if self.starts_at < timezone.now and timezone.now < self.expires_at:
    #        return True
    #    return False

    def __str__(self):
        return f"{self.title}"
    
class Question(models.Model):

    class State(models.TextChoices):
        NEW = "new", _("New")
        APPROVED = "approved", _("Approved")
        ANSWERED = "answered", _("Answered")
        DISCARDED = "discarded", _("Discarded")

    text = models.TextField(max_length=1000)
    state = models.CharField(
        max_length = 9,
        choices = State.choices,
        default = State.NEW
    )
    
    created_at = models.DateTimeField("Date asked", default=timezone.now)
    created_by = models.CharField(max_length=200)
    display_name = models.CharField(max_length=50)
    voxpop = models.ForeignKey(Voxpop, on_delete=models.CASCADE)

    def approve(self):
        self.state = State.APPROVED
        self.save()

    def get_votes(self):
        return Vote.objects.filter(question_id=self.id).count()

    # TODO: As Ninja Schema?
    def as_dict(self):
        return ({
            "id": self.id,
            "topic": self.topic.title,
            "text": self.text,
            "created_at": self.created_at,
            "created_by": self.created_by,
            "state": self.state,
            "vote_count": self.get_votes(),
        })

    def __str__(self):
        return f'[{self.created_at.time()}]: "{self.text}" ({self.state})'

class Vote(models.Model):

    created_by = models.CharField(max_length=200)
    created_at = models.DateTimeField("Date voted", default=timezone.now)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.created_by} -> "{self.question.text}"'