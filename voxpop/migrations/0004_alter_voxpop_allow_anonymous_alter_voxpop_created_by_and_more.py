# Generated by Django 4.2 on 2023-08-23 07:31

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("voxpop", "0003_alter_question_display_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="voxpop",
            name="allow_anonymous",
            field=models.BooleanField(default=False, verbose_name="allow anonymous"),
        ),
        migrations.AlterField(
            model_name="voxpop",
            name="created_by",
            field=models.CharField(max_length=50, verbose_name="created by"),
        ),
        migrations.AlterField(
            model_name="voxpop",
            name="description",
            field=models.TextField(blank=True, verbose_name="description"),
        ),
        migrations.AlterField(
            model_name="voxpop",
            name="expires_at",
            field=models.DateTimeField(verbose_name="end time"),
        ),
        migrations.AlterField(
            model_name="voxpop",
            name="is_moderated",
            field=models.BooleanField(default=True, verbose_name="is moderated"),
        ),
        migrations.AlterField(
            model_name="voxpop",
            name="starts_at",
            field=models.DateTimeField(verbose_name="start time"),
        ),
        migrations.AlterField(
            model_name="voxpop",
            name="title",
            field=models.CharField(max_length=50, verbose_name="voxpop title"),
        ),
    ]
