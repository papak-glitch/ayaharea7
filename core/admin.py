from django.contrib import admin
from .models import *
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
# admin.py
from django.contrib import admin
from .models import Leader
from django.contrib import admin
from django.contrib import admin
from .models import MediaAlbum, MediaImage
from django.contrib import admin
from .models import Notification

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
