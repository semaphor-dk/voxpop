from django.contrib import admin

from .models import Question, Vote, Voxpop, Organisation

# Register your models here.
admin.site.register(Organisation)
admin.site.register(Voxpop)
admin.site.register(Question)
admin.site.register(Vote)