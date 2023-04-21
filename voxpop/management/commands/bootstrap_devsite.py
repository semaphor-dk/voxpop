from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management import BaseCommand
from django.utils import timezone

from voxpop.models import Organisation
from voxpop.models import Question
from voxpop.models import Vote
from voxpop.models import Voxpop


class Command(BaseCommand):
    help = "Bootstrap a development site with some initial data"

    def handle(self, *args, **options):
        # Flush database
        self.stdout.write("Flushing database...")
        self.flush_database()

        # Create initial data
        self.create_users()
        self.create_organisations()
        self.create_voxpop()
        self.create_questions()
        self.create_votes()

    def flush_database(self):
        # Flush database by calling django management command
        from django.core.management import call_command

        call_command("flush", interactive=False)

    def create_users(self):
        self.stdout.write("Creating users...")
        # Create a user
        self.admin_user = User.objects.create_superuser(
            username="admin",
            password="admin",
        )

    def create_organisations(self):
        self.stdout.write("Creating organisations...")
        self.organisations = [
            Organisation.objects.create(
                name="Organisation",
            ),
        ]

    def create_voxpop(self):
        self.stdout.write("Creating voxpops...")
        self.voxpops = [
            Voxpop.objects.create(
                title="Voxpop",
                description="Voxpop description",
                created_by=self.admin_user,
                starts_at=timezone.now(),
                expires_at=timezone.now() + timedelta(days=7),
                is_moderated=True,
                allow_anonymous=False,
                organisation=self.organisations[0],
            ),
        ]

    def create_questions(self):
        self.stdout.write("Creating questions...")
        self.questions = [
            Question.objects.create(
                text="Question 1",
                created_by="user8",
                display_name="Question 1",
                voxpop=self.voxpops[0],
            ),
            Question.objects.create(
                text="Question 2",
                created_by="user4",
                display_name="Question 2",
                voxpop=self.voxpops[0],
                state=Question.State.APPROVED,
            ),
            Question.objects.create(
                text="Question 3",
                created_by="user5",
                display_name="Question 3",
                voxpop=self.voxpops[0],
            ),
        ]

    def create_votes(self):
        self.stdout.write("Creating votes...")
        self.votes = [
            Vote.objects.create(
                question=self.questions[1],
                created_by="user1",
            ),
            Vote.objects.create(
                question=self.questions[1],
                created_by="user2",
            ),
        ]
