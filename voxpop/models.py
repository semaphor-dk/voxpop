import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


class UUIDModel(models.Model):
    uuid = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    class Meta:
        abstract = True


class CreatedUpdatedMixin(UUIDModel):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Organisation(CreatedUpdatedMixin):
    # Work in progress.
    name = models.CharField(max_length=200)
    hostname = models.CharField(
        max_length=200,
        null=True,
        blank=True,
    )
    idp = models.CharField(
        max_length=200,
        null=True,
        blank=True,
    )
    admin_group = models.CharField(
        max_length=200,
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name


class Voxpop(CreatedUpdatedMixin):
    title = models.CharField(max_length=50)  # evt. topic
    description = models.TextField(blank=True)
    created_by = models.CharField(max_length=50)
    starts_at = models.DateTimeField("Starttime")
    expires_at = models.DateTimeField("Endtime")
    is_moderated = models.BooleanField(default=True)
    allow_anonymous = models.BooleanField(default=False)
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, related_name='voxpops')

    def __str__(self):
        return f"{self.title}"


class Question(CreatedUpdatedMixin):
    class State(models.TextChoices):
        NEW = "new", _("New")
        APPROVED = "approved", _("Approved")
        ANSWERED = "answered", _("Answered")
        DISCARDED = "discarded", _("Discarded")

    text = models.TextField(max_length=1000)
    state = models.CharField(
        max_length=9,
        choices=State.choices,
        default=State.NEW,
    )
    created_by = models.CharField(max_length=200)
    display_name = models.CharField(blank=True, max_length=50)
    voxpop = models.ForeignKey(Voxpop, on_delete=models.CASCADE, related_name='questions')

    def approve(self):
        self.state = self.State.APPROVED
        self.save()

    def __str__(self):
        return f'[{self.created_at.strftime("%H:%M")}] "{self.text}"'


class Vote(CreatedUpdatedMixin):
    created_by = models.CharField(max_length=200)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="votes")

    def __str__(self):
        return f'{self.created_by} -> "{self.question.text}"'
