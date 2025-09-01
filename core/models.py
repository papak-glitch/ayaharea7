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



class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    link = models.URLField(blank=True, null=True)
    notification_type = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.user.username}"    


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
    
# models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class BibleVerse(models.Model):
    text = models.TextField()
    reference = models.CharField(max_length=100)
    book = models.CharField(max_length=50)
    chapter = models.IntegerField()
    verse_start = models.IntegerField()
    verse_end = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_daily = models.BooleanField(default=False)
    daily_date = models.DateField(null=True, blank=True, unique=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['daily_date']),
            models.Index(fields=['is_daily']),
        ]
    
    def __str__(self):
        return f"{self.reference}: {self.text[:50]}..."
    
    @property
    def total_likes(self):
        """Get total likes from both authenticated and anonymous users"""
        auth_likes = self.likes.count()
        anon_likes = AnonymousVerseInteraction.objects.filter(
            verse=self, interaction_type='like'
        ).count()
        return auth_likes + anon_likes
    
    @property
    def total_shares(self):
        """Get total shares from both authenticated and anonymous users"""
        auth_shares = self.shares.count()
        anon_shares = AnonymousVerseInteraction.objects.filter(
            verse=self, interaction_type='share'
        ).count()
        return auth_shares + anon_shares
    
    def user_has_liked(self, user=None, ip_address=None, session_key=None):
        """Check if user has liked this verse"""
        if user and user.is_authenticated:
            return self.likes.filter(user=user).exists()
        elif ip_address and session_key:
            return AnonymousVerseInteraction.objects.filter(
                verse=self,
                ip_address=ip_address,
                session_key=session_key,
                interaction_type='like'
            ).exists()
        return False

class VerseLike(models.Model):
    """Likes from authenticated users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    verse = models.ForeignKey(BibleVerse, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        unique_together = ('user', 'verse')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} likes {self.verse.reference}"

class VerseShare(models.Model):
    """Shares from authenticated users"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    verse = models.ForeignKey(BibleVerse, on_delete=models.CASCADE, related_name='shares')
    created_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    share_method = models.CharField(
        max_length=20,
        choices=[
            ('native', 'Native Share'),
            ('clipboard', 'Clipboard'),
            ('social', 'Social Media'),
        ],
        default='clipboard'
    )
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        user_display = self.user.username if self.user else f"Anonymous ({self.ip_address})"
        return f"{user_display} shared {self.verse.reference}"

class AnonymousVerseInteraction(models.Model):
    """Interactions from anonymous users (likes and shares)"""
    verse = models.ForeignKey(BibleVerse, on_delete=models.CASCADE, related_name='anonymous_interactions')
    ip_address = models.GenericIPAddressField()
    session_key = models.CharField(max_length=40, null=True, blank=True)
    interaction_type = models.CharField(
        max_length=10,
        choices=[('like', 'Like'), ('share', 'Share')]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    user_agent = models.TextField(null=True, blank=True)  # Optional: track device info
    
    class Meta:
        # Allow only one like per IP+session+verse, but multiple shares
        indexes = [
            models.Index(fields=['verse', 'interaction_type']),
            models.Index(fields=['ip_address', 'session_key']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Anonymous {self.interaction_type} for {self.verse.reference} from {self.ip_address}"
    
    def save(self, *args, **kwargs):
        # For likes, ensure uniqueness per IP+session+verse
        if self.interaction_type == 'like':
            existing = AnonymousVerseInteraction.objects.filter(
                verse=self.verse,
                ip_address=self.ip_address,
                session_key=self.session_key,
                interaction_type='like'
            ).exclude(pk=self.pk)
            
            if existing.exists():
                # Delete existing like before creating new one
                existing.delete()
        
        super().save(*args, **kwargs)