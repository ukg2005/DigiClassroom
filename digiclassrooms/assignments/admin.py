from django.contrib import admin
from .models import Assignment, Question, Choice, StudentAnswer, Submission, SubmissionDraft, DeadlineEvent

admin.site.register(Assignment)
admin.site.register(Question)
admin.site.register(Choice)
admin.site.register(StudentAnswer)
admin.site.register(Submission)
admin.site.register(SubmissionDraft)
admin.site.register(DeadlineEvent)