# Generated by Django 4.2 on 2023-06-29 14:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voxpop', '0002_alter_question_display_name_alter_question_voxpop_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='display_name',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
