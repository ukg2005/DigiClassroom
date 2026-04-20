from django.contrib import admin
from .models import Lecture, LectureComment

admin.site.register(Lecture)
admin.site.register(LectureComment)