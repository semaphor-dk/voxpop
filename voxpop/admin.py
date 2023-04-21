from django.contrib import admin

from .models import Organisation
from .models import Question
from .models import Vote
from .models import Voxpop

# Register your models here.
admin.site.register(Organisation)
admin.site.register(Voxpop)
admin.site.register(Question)
admin.site.register(Vote)
