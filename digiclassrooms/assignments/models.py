from django.db import models
from django.contrib.auth.models import User
from classrooms.models import Classroom
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.db.models.manager import RelatedManager

class Assignment(models.Model):
    ASSIGNMENT_TYPE_QUIZ = 'quiz'
    ASSIGNMENT_TYPE_QNA = 'qna'
    ASSIGNMENT_TYPE_CHOICES = [
        (ASSIGNMENT_TYPE_QUIZ, 'Quiz'),
        (ASSIGNMENT_TYPE_QNA, 'Q&A'),
    ]

    LATE_POLICY_ALLOW = 'allow'
    LATE_POLICY_DENY = 'deny'
    LATE_POLICY_PENALTY = 'penalty'
    LATE_POLICY_CHOICES = [
        (LATE_POLICY_ALLOW, 'Allow'),
        (LATE_POLICY_DENY, 'Deny'),
        (LATE_POLICY_PENALTY, 'Allow with penalty'),
    ]

    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=200)
    assignment_type = models.CharField(max_length=10, choices=ASSIGNMENT_TYPE_CHOICES, default=ASSIGNMENT_TYPE_QUIZ)
    prompt = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateTimeField(null=True, blank=True)
    late_submission_policy = models.CharField(max_length=10, choices=LATE_POLICY_CHOICES, default=LATE_POLICY_DENY)
    late_penalty_percent = models.PositiveIntegerField(default=0)
    max_attempts = models.PositiveIntegerField(default=1)
    
    if TYPE_CHECKING:
        id: int
        questions: 'RelatedManager[Question]'
        submissions: 'RelatedManager[Submission]'

    def __str__(self):
        return self.title

    @property
    def is_quiz(self):
        return self.assignment_type == self.ASSIGNMENT_TYPE_QUIZ

class Question(models.Model):
    QUESTION_TYPE_MCQ = 'mcq'
    QUESTION_TYPE_QNA = 'qna'
    QUESTION_TYPE_CHOICES = [
        (QUESTION_TYPE_MCQ, 'Multiple Choice'),
        (QUESTION_TYPE_QNA, 'Q&A'),
    ]

    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='questions')
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPE_CHOICES, default=QUESTION_TYPE_MCQ)
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
    attempt_number = models.PositiveIntegerField(default=1)
    score = models.IntegerField(default=0)
    teacher_feedback = models.TextField(blank=True, null=True)
    text_response = models.TextField(blank=True)
    is_late = models.BooleanField(default=False)
    late_penalty_percent = models.PositiveIntegerField(default=0)
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    if TYPE_CHECKING:
        id: int
        answers: 'RelatedManager[StudentAnswer]'

    def __str__(self):
        return f'{self.student.username} - {self.assignment.title}'

class StudentAnswer(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE, null=True, blank=True)
    text_response = models.TextField(blank=True)


class SubmissionDraft(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='drafts')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assignment_drafts')
    answers = models.JSONField(default=dict)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('assignment', 'student')


class DeadlineEvent(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='deadline_events')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    due_date = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_deadline_events')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['due_date', 'created_at']

    def __str__(self):
        return f'{self.title} - {self.classroom.name}'
