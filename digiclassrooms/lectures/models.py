from django.db import models
from django.contrib.auth.models import User
from classrooms.models import Classroom
from typing import TYPE_CHECKING
from urllib.parse import parse_qs, urlparse

if TYPE_CHECKING:
    from django.db.models.manager import RelatedManager

class Lecture(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='lectures')
    title = models.CharField(max_length=200)
    youtube_link = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_thread_locked = models.BooleanField(default=False)
    
    if TYPE_CHECKING:
        id: int
        comments: 'RelatedManager[LectureComment]'

    def __str__(self):
        return self.title
        
    def get_video_id(self):
        if not self.youtube_link:
            return ''

        raw = self.youtube_link.strip()
        parsed = urlparse(raw)
        host = parsed.netloc.lower().replace('www.', '')
        path_parts = [part for part in parsed.path.split('/') if part]

        video_id = ''

        if host == 'youtu.be' and path_parts:
            video_id = path_parts[0]
        elif host in {'youtube.com', 'm.youtube.com', 'music.youtube.com', 'youtube-nocookie.com'}:
            if path_parts and path_parts[0] == 'watch':
                query = parse_qs(parsed.query)
                video_id = (query.get('v') or [''])[0]
            elif path_parts and path_parts[0] in {'embed', 'v', 'shorts', 'live'} and len(path_parts) > 1:
                video_id = path_parts[1]

        video_id = (video_id or '').strip()

        # YouTube video IDs are 11 characters in practice; reject malformed IDs.
        if len(video_id) != 11:
            return ''

        return video_id

class LectureComment(models.Model):
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_edited = models.BooleanField(default=False)
    
    if TYPE_CHECKING:
        id: int
        replies: 'RelatedManager[LectureComment]'

    def __str__(self):
        return f'Comment by {self.author.username} on {self.lecture.title}'
