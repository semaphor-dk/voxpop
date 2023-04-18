from django.contrib import admin

from .models import Question, Vote

# Register your models here.
admin.site.register(Question)
admin.site.register(Vote)
