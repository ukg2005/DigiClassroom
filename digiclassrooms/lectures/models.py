from django.db import models
from django.contrib.auth.models import User
from classrooms.models import Classroom
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.db.models.manager import RelatedManager

class Lecture(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='lectures')
    title = models.CharField(max_length=200)
    youtube_link = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    if TYPE_CHECKING:
        id: int
        comments: 'RelatedManager[LectureComment]'

    def __str__(self):
        return self.title
        
    def get_video_id(self):
        if not self.youtube_link:
            return ''
        
        url = self.youtube_link.strip()
        video_id = ''
        
        if 'youtu.be/' in url:
            video_id = url.split('youtu.be/')[-1]
            if '/' in video_id:
                video_id = video_id.split('/')[0]
            video_id = video_id.split('?')[0].split('&')[0].split('#')[0]
        elif 'youtube.com/watch' in url:
            if 'v=' in url:
                video_id = url.split('v=')[1]
                video_id = video_id.split('&')[0].split('#')[0]
        elif 'youtube.com/embed/' in url:
            video_id = url.split('embed/')[-1]
            video_id = video_id.split('?')[0].split('/')[0]
        elif 'youtube.com/v/' in url:
            video_id = url.split('v/')[-1]
            video_id = video_id.split('?')[0].split('/')[0]
            
        return video_id.strip()

class LectureComment(models.Model):
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)
    
    if TYPE_CHECKING:
        id: int
        replies: 'RelatedManager[LectureComment]'

    def __str__(self):
        return f'Comment by {self.author.username} on {self.lecture.title}'
