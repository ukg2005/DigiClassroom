from django.db import models
from django.contrib.auth.models import User
from classrooms.models import Classroom
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.db.models.manager import RelatedManager

class Assignment(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    
    if TYPE_CHECKING:
        id: int
        questions: 'RelatedManager[Question]'
        submissions: 'RelatedManager[Submission]'

    def __str__(self):
        return self.title

class Question(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField(max_length=500)
    
    if TYPE_CHECKING:
        id: int
        choices: 'RelatedManager[Choice]'
    
    def __str__(self):
        return self.text

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)
    
    def __str__(self):
        return self.text

class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    score = models.IntegerField(default=0)
    teacher_feedback = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    if TYPE_CHECKING:
        id: int
        answers: 'RelatedManager[StudentAnswer]'

    def __str__(self):
        return f'{self.student.username} - {self.assignment.title}'

class StudentAnswer(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
