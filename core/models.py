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



# models.py

from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.db.models import Count, Q
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

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

    @property
    def like_counts(self):
        """Get like and dislike counts for this event"""
        counts = self.reactions.aggregate(
            likes=Count('id', filter=Q(reaction='like')),
            dislikes=Count('id', filter=Q(reaction='dislike'))
        )
        return {
            'likes': counts['likes'] or 0,
            'dislikes': counts['dislikes'] or 0
        }

    @property
    def total_likes(self):
        """Get total number of likes"""
        return self.reactions.filter(reaction='like').count()

    @property
    def total_dislikes(self):
        """Get total number of dislikes"""
        return self.reactions.filter(reaction='dislike').count()

    def get_user_reaction(self, device_id):
        """Get the reaction (like/dislike) for a specific device"""
        try:
            reaction = self.reactions.get(device_id=device_id)
            return reaction.reaction
        except EventLike.DoesNotExist:
            return None

    def has_user_liked(self, device_id):
        """Check if a device has liked this event"""
        return self.reactions.filter(device_id=device_id, reaction='like').exists()

    def has_user_disliked(self, device_id):
        """Check if a device has disliked this event"""
        return self.reactions.filter(device_id=device_id, reaction='dislike').exists()

    class Meta:
        ordering = ['date', 'time']


class EventLike(models.Model):
    REACTION_CHOICES = [
        ('like', 'Like'),
        ('dislike', 'Dislike'),
    ]
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='reactions')
    device_id = models.CharField(max_length=100, help_text="Unique identifier for the device/browser")
    reaction = models.CharField(max_length=10, choices=REACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['event', 'device_id']  # One reaction per device per event
        indexes = [
            models.Index(fields=['event', 'reaction']),  # For faster count queries
            models.Index(fields=['device_id']),
        ]
    
    def __str__(self):
        return f"{self.device_id} {self.reaction}d {self.event.title}"

    def save(self, *args, **kwargs):
        # Ensure reaction is lowercase
        self.reaction = self.reaction.lower()
        super().save(*args, **kwargs)

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




from django.db import models
from django.contrib.auth.models import User


  
class GalleryImage(models.Model):
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='gallery/')
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return self.title or f"Gallery Image {self.id}"
    
from django.db import models
from django.utils import timezone
import uuid

class BibleVerse(models.Model):
    reference = models.CharField(max_length=100, unique=True)
    text = models.TextField()
    date = models.DateField(default=timezone.now)
    like_count = models.PositiveIntegerField(default=0)
    share_count = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.reference

class VerseInteraction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    verse = models.ForeignKey(BibleVerse, on_delete=models.CASCADE, related_name='interactions')
    session_key = models.CharField(max_length=40, db_index=True)
    liked = models.BooleanField(default=False)
    shared = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        # Use indexes instead of unique_together to avoid the constraint error
        indexes = [
            models.Index(fields=['verse', 'session_key']),
        ]
    
    def __str__(self):
        return f"{self.verse.reference} - {self.session_key}"