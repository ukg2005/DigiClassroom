from django.db import models
from django.contrib.auth.models import User
from classrooms.models import Classroom
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.db.models.manager import RelatedManager

class Notice(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='notices')
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    if TYPE_CHECKING:
        id: int
        comments: 'RelatedManager[NoticeComment]'

    def __str__(self):
        return self.title

class NoticeComment(models.Model):
    notice = models.ForeignKey(Notice, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)
    
    if TYPE_CHECKING:
        id: int
        replies: 'RelatedManager[NoticeComment]'

    def __str__(self):
        return f'Comment by {self.author.username} on {self.notice.title}'
