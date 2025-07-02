from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
import uuid
from django.db import migrations
from django.urls import reverse
from django.contrib.auth import get_user_model
User = get_user_model()

# Create your models here.


        # events/models.py
from django.db import models
from django.utils import timezone
from django.urls import reverse
# models.py
from django.db import models
# models.py
from django.db import models


class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=200)
    image = models.ImageField(upload_to='events/images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('event_detail', kwargs={'pk': self.pk})

    @property
    def is_upcoming(self):
        today = timezone.now().date()
        return self.date >= today

    class Meta:
        ordering = ['date', 'time']

from django.contrib.auth import get_user_model
User = get_user_model()

class Comment(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='comments')
    author_name = models.CharField(max_length=100)  # For non-authenticated users
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')


    def __str__(self):
        return f"Comment by {self.author_name} on {self.event.title}"
    
    @property
    def is_reply(self):
        return self.parent is not None



class Leader(models.Model):
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    bio = models.TextField()
    email = models.EmailField()
    image = models.ImageField(upload_to='leaders/')
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)  # For manual ordering
    
    class Meta:
        ordering = ['order', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.position}"
    


from django.db import models

class MediaAlbum(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    date_taken = models.DateField()
    is_recent = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class MediaImage(models.Model):
    album = models.ForeignKey(MediaAlbum, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='media_gallery/')
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"Image {self.id} for {self.album.title}"

class MediaImage(models.Model):
    album = models.ForeignKey(MediaAlbum, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='media_gallery/')
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"Image {self.id} for {self.album.title}"        
  
