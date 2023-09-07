# Generated by Django 4.2 on 2023-09-06 14:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('voxpop', '0005_alter_voxpop_title'),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event', models.CharField(max_length=255)),
                ('data', models.TextField()),
                ('voxpop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='voxpop.voxpop')),
            ],
        ),
    ]