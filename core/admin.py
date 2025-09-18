from django.contrib import admin
from .models import *
from django.contrib import admin

# admin.py
from .models import Leader

from .models import MediaAlbum, MediaImage
from django.contrib import admin
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


    

@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ['title', 'order', 'created_at']
    list_editable = ['order']
    list_filter = ['created_at']
    search_fields = ['title', 'description']


# admin.py
from django.contrib import admin
from .models import BibleVerse, VerseInteraction

@admin.register(BibleVerse)
class BibleVerseAdmin(admin.ModelAdmin):
    list_display = ('reference', 'date', 'like_count', 'share_count', 'text_preview')
    list_filter = ('date',)
    search_fields = ('reference', 'text')
    readonly_fields = ('like_count', 'share_count')
    
    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Text Preview'

@admin.register(VerseInteraction)
class VerseInteractionAdmin(admin.ModelAdmin):
    list_display = ('verse', 'session_key', 'liked', 'shared', 'created_at')
    list_filter = ('liked', 'shared', 'created_at', 'verse')
    search_fields = ('verse__reference', 'session_key')
    readonly_fields = ('created_at',)