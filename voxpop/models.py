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
    title = models.CharField(_("title"), max_length=50)
    description = models.TextField(_("description"), blank=True)
    created_by = models.CharField(_("created by"), max_length=50,)
    starts_at = models.DateTimeField(_("start time"))
    expires_at = models.DateTimeField(_("end time"))
    is_moderated = models.BooleanField(_("is moderated"), default=True)
    allow_anonymous = models.BooleanField(_("allow anonymous"), default=False)
    organisation = models.ForeignKey(
            Organisation,
            on_delete=models.CASCADE,
            related_name='voxpops',
            )

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

class Message(models.Model):
    voxpop = models.ForeignKey(Voxpop, on_delete=models.CASCADE, related_name='messages')
    channel_name = models.CharField(max_length=255, default="")
    event = models.CharField(max_length=255)
    data = models.TextField()

    def __str__(self):
        return f"id: {self.id}\nevent: {self.event}\ndata: {self.data}\n\n"
