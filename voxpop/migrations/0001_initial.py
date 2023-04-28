# Generated by Django 4.2 on 2023-04-26 12:32

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Organisation",
            fields=[
                (
                    "uuid",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=200)),
                ("hostname", models.CharField(blank=True, max_length=200, null=True)),
                ("idp", models.CharField(blank=True, max_length=200, null=True)),
                (
                    "admin_group",
                    models.CharField(blank=True, max_length=200, null=True),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Question",
            fields=[
                (
                    "uuid",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("text", models.TextField(max_length=1000)),
                (
                    "state",
                    models.CharField(
                        choices=[
                            ("new", "New"),
                            ("approved", "Approved"),
                            ("answered", "Answered"),
                            ("discarded", "Discarded"),
                        ],
                        default="new",
                        max_length=9,
                    ),
                ),
                ("created_by", models.CharField(max_length=200)),
                ("display_name", models.CharField(max_length=50)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Voxpop",
            fields=[
                (
                    "uuid",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=50)),
                ("description", models.TextField(blank=True)),
                ("created_by", models.CharField(max_length=50)),
                ("starts_at", models.DateTimeField(verbose_name="Starttime")),
                ("expires_at", models.DateTimeField(verbose_name="Endtime")),
                ("is_moderated", models.BooleanField(default=True)),
                ("allow_anonymous", models.BooleanField(default=False)),
                (
                    "organisation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="voxpop.organisation",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Vote",
            fields=[
                (
                    "uuid",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_by", models.CharField(max_length=200)),
                (
                    "question",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="votes",
                        to="voxpop.question",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="question",
            name="voxpop",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="voxpop.voxpop",
            ),
        ),
    ]
