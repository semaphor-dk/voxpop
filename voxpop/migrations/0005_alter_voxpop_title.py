# Generated by Django 4.2 on 2023-08-28 10:41

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "voxpop",
            "0004_alter_voxpop_allow_anonymous_alter_voxpop_created_by_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="voxpop",
            name="title",
            field=models.CharField(max_length=50, verbose_name="title"),
        ),
    ]
