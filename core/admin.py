from django.contrib import admin
from .models import *
from django.contrib import admin

# admin.py
from .models import Leader

from .models import MediaAlbum, MediaImage
from django.contrib import admin
from .models import Notification, BibleVerse, AnonymousVerseInteraction, VerseLike, VerseShare
from django.utils.html import format_html
from django.utils import timezone
from django.urls import reverse
from django.utils.safestring import mark_safe

# Register your models here.
admin.site.register(Event)
class LeaderAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    search_fields = ('name', 'position')
    list_filter = ('is_active',)
    fieldsets = (
        (None, {
            'fields': ('name', 'position', 'bio', 'email', 'image', 'is_active', 'order')
        }),
    )

admin.site.register(Leader, LeaderAdmin)





class MediaImageInline(admin.TabularInline):
    model = MediaImage
    extra = 3
    fields = ('image', 'caption', 'order')

@admin.register(MediaAlbum)
class MediaAlbumAdmin(admin.ModelAdmin):
    inlines = [MediaImageInline]
    list_display = ('title', 'date_taken', 'is_recent')
    list_filter = ('is_recent', 'date_taken')
    search_fields = ('title', 'description')
    date_hierarchy = 'date_taken'



@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at', 'user')
    search_fields = ('title', 'message', 'user__username')
    date_hierarchy = 'created_at'    

@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ['title', 'order', 'created_at']
    list_editable = ['order']
    list_filter = ['created_at']
    search_fields = ['title', 'description']


# admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from django.utils import timezone
from django.urls import reverse
from django.utils.safestring import mark_safe

@admin.register(BibleVerse)
class BibleVerseAdmin(admin.ModelAdmin):
    list_display = [
        'reference', 
        'text_preview', 
        'is_daily', 
        'daily_date',
        'total_likes_display',
        'total_shares_display',
        'view_interactions_link',
        'created_at'
    ]
    list_filter = [
        'is_daily', 
        'daily_date', 
        'book', 
        'created_at'
    ]
    search_fields = [
        'text', 
        'reference', 
        'book'
    ]
    readonly_fields = [
        'total_likes_display', 
        'total_shares_display',
        'interactions_summary',
        'created_at'
    ]
    ordering = ['-daily_date', '-created_at']
    date_hierarchy = 'daily_date'
    list_per_page = 20
    
    fieldsets = (
        ('Verse Content', {
            'fields': ('text', 'reference', 'book', 'chapter', 'verse_start', 'verse_end')
        }),
        ('Daily Verse Settings', {
            'fields': ('is_daily', 'daily_date'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('total_likes_display', 'total_shares_display', 'interactions_summary'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    def text_preview(self, obj):
        return obj.text[:75] + "..." if len(obj.text) > 75 else obj.text
    text_preview.short_description = "Text Preview"
    
    def total_likes_display(self, obj):
        auth_likes = obj.likes.count()
        anon_likes = AnonymousVerseInteraction.objects.filter(
            verse=obj, interaction_type='like'
        ).count()
        total = auth_likes + anon_likes
        return format_html(
            '<strong style="color: #e74c3c;">{}</strong> <small style="color: #7f8c8d;">(👤 {} | 👥 {})</small>',
            total, auth_likes, anon_likes
        )
    total_likes_display.short_description = "❤️ Total Likes"
    
    def total_shares_display(self, obj):
        auth_shares = obj.shares.count()
        anon_shares = AnonymousVerseInteraction.objects.filter(
            verse=obj, interaction_type='share'
        ).count()
        total = auth_shares + anon_shares
        return format_html(
            '<strong style="color: #3498db;">{}</strong> <small style="color: #7f8c8d;">(👤 {} | 👥 {})</small>',
            total, auth_shares, anon_shares
        )
    total_shares_display.short_description = "📤 Total Shares"
    
    def view_interactions_link(self, obj):
        like_url = reverse('admin:bible_verselike_changelist') + f'?verse__id__exact={obj.id}'
        share_url = reverse('admin:bible_verseshare_changelist') + f'?verse__id__exact={obj.id}'
        anon_url = reverse('admin:bible_anonymousverseinteraction_changelist') + f'?verse__id__exact={obj.id}'
        
        return format_html(
            '<a href="{}" style="color: #e74c3c;">👤 Likes</a> | '
            '<a href="{}" style="color: #3498db;">👤 Shares</a> | '
            '<a href="{}" style="color: #f39c12;">👥 Anonymous</a>',
            like_url, share_url, anon_url
        )
    view_interactions_link.short_description = "View Interactions"
    
    def interactions_summary(self, obj):
        recent_likes = VerseLike.objects.filter(verse=obj).order_by('-created_at')[:3]
        recent_shares = VerseShare.objects.filter(verse=obj).order_by('-created_at')[:3]
        recent_anon = AnonymousVerseInteraction.objects.filter(verse=obj).order_by('-created_at')[:3]
        
        summary = "<h3>Recent Activity:</h3>"
        
        if recent_likes:
            summary += "<h4>Recent Likes:</h4><ul>"
            for like in recent_likes:
                summary += f"<li>{like.user.username} - {like.created_at.strftime('%Y-%m-%d %H:%M')}</li>"
            summary += "</ul>"
        
        if recent_anon:
            summary += "<h4>Recent Anonymous Activity:</h4><ul>"
            for anon in recent_anon:
                summary += f"<li>{anon.interaction_type.title()} from {anon.ip_address} - {anon.created_at.strftime('%Y-%m-%d %H:%M')}</li>"
            summary += "</ul>"
        
        return mark_safe(summary) if recent_likes or recent_anon else "No recent activity"
    interactions_summary.short_description = "Recent Activity"
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('likes', 'shares', 'anonymous_interactions')
    
    actions = ['mark_as_daily', 'unmark_as_daily', 'set_daily_date_today']
    
    def mark_as_daily(self, request, queryset):
        updated = queryset.update(is_daily=True)
        self.message_user(request, f'{updated} verses marked as daily.')
    mark_as_daily.short_description = "✅ Mark selected verses as daily"
    
    def unmark_as_daily(self, request, queryset):
        updated = queryset.update(is_daily=False)
        self.message_user(request, f'{updated} verses unmarked as daily.')
    unmark_as_daily.short_description = "❌ Unmark selected verses as daily"
    
    def set_daily_date_today(self, request, queryset):
        today = timezone.now().date()
        updated = queryset.update(daily_date=today, is_daily=True)
        self.message_user(request, f'{updated} verses set with today\'s date as daily verse.')
    set_daily_date_today.short_description = "📅 Set daily date to today"

@admin.register(VerseLike)
class VerseLikeAdmin(admin.ModelAdmin):
    list_display = [
        'user_link', 
        'verse_reference', 
        'created_at',
        'ip_address'
    ]
    list_filter = [
        'created_at',
        'verse__book',
        'verse__is_daily'
    ]
    search_fields = [
        'user__username',
        'user__email', 
        'verse__reference',
        'verse__text',
        'ip_address'
    ]
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    list_per_page = 25
    
    def user_link(self, obj):
        url = reverse('admin:auth_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = "User"
    user_link.admin_order_field = 'user__username'
    
    def verse_reference(self, obj):
        url = reverse('admin:bible_bibleverse_change', args=[obj.verse.id])
        return format_html('<a href="{}">{}</a>', url, obj.verse.reference)
    verse_reference.short_description = "Verse"
    verse_reference.admin_order_field = 'verse__reference'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'verse')

@admin.register(VerseShare)
class VerseShareAdmin(admin.ModelAdmin):
    list_display = [
        'user_display', 
        'verse_reference', 
        'share_method',
        'created_at',
        'ip_address'
    ]
    list_filter = [
        'share_method',
        'created_at',
        'verse__book',
        'verse__is_daily'
    ]
    search_fields = [
        'user__username',
        'user__email',
        'verse__reference',
        'verse__text',
        'ip_address'
    ]
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    list_per_page = 25
    
    def user_display(self, obj):
        if obj.user:
            url = reverse('admin:auth_user_change', args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return f"Anonymous ({obj.ip_address})"
    user_display.short_description = "User"
    user_display.admin_order_field = 'user__username'
    
    def verse_reference(self, obj):
        url = reverse('admin:bible_bibleverse_change', args=[obj.verse.id])
        return format_html('<a href="{}">{}</a>', url, obj.verse.reference)
    verse_reference.short_description = "Verse"
    verse_reference.admin_order_field = 'verse__reference'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'verse')

@admin.register(AnonymousVerseInteraction)
class AnonymousVerseInteractionAdmin(admin.ModelAdmin):
    list_display = [
        'ip_session_display',
        'verse_reference', 
        'interaction_type',
        'created_at',
        'device_info'
    ]
    list_filter = [
        'interaction_type',
        'created_at',
        'verse__book',
        'verse__is_daily'
    ]
    search_fields = [
        'ip_address',
        'session_key',
        'verse__reference',
        'verse__text'
    ]
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    list_per_page = 25
    
    def ip_session_display(self, obj):
        session_short = obj.session_key[:8] if obj.session_key else 'No Session'
        return format_html(
            '<strong>{}</strong><br><small>Session: {}...</small>',
            obj.ip_address, session_short
        )
    ip_session_display.short_description = "IP & Session"
    
    def verse_reference(self, obj):
        url = reverse('admin:bible_bibleverse_change', args=[obj.verse.id])
        return format_html('<a href="{}">{}</a>', url, obj.verse.reference)
    verse_reference.short_description = "Verse"
    verse_reference.admin_order_field = 'verse__reference'
    
    def device_info(self, obj):
        if obj.user_agent:
            # Extract browser info (simplified)
            ua = obj.user_agent.lower()
            if 'chrome' in ua:
                browser = 'Chrome'
            elif 'firefox' in ua:
                browser = 'Firefox'
            elif 'safari' in ua:
                browser = 'Safari'
            elif 'edge' in ua:
                browser = 'Edge'
            else:
                browser = 'Other'
                
            # Check if mobile
            is_mobile = any(mobile in ua for mobile in ['mobile', 'android', 'iphone', 'ipad'])
            device_type = 'Mobile' if is_mobile else 'Desktop'
            
            return f"{browser} ({device_type})"
        return "Unknown"
    device_info.short_description = "Device"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('verse')

# Customize admin site header and title
admin.site.site_header = "Bible Verse Administration"
admin.site.site_title = "Bible Admin"
admin.site.index_title = "Welcome to Bible Verse Management"

# Add custom CSS to admin
class BibleAdminConfig:
    def ready(self):
        pass

# Optional: Custom admin actions
def export_verse_stats(modeladmin, request, queryset):
    """Export verse statistics as CSV"""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="verse_stats.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Reference', 'Text Preview', 'Total Likes', 'Total Shares', 'Is Daily', 'Daily Date'])
    
    for verse in queryset:
        writer.writerow([
            verse.reference,
            verse.text[:100],
            verse.total_likes,
            verse.total_shares,
            verse.is_daily,
            verse.daily_date
        ])
    
    return response

export_verse_stats.short_description = "📊 Export verse statistics"

# Add the export action to BibleVerse admin
BibleVerseAdmin.actions.append(export_verse_stats)



