from django.db import models
from django.contrib.auth.models import User
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.db.models.manager import RelatedManager
    from notices.models import Notice
    from lectures.models import Lecture
    from assignments.models import Assignment

class Classroom(models.Model):
    name = models.CharField(max_length=100)
    teacher = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teaching_classroom')
    students = models.ManyToManyField(User, related_name='enrolled_classrooms', blank=True)
    description = models.TextField(blank=True)
    
    if TYPE_CHECKING:
        id: int
        pk: int
        notices: 'RelatedManager[Notice]'
        lectures: 'RelatedManager[Lecture]'
        assignments: 'RelatedManager[Assignment]'

    def __str__(self):
        return self.name
