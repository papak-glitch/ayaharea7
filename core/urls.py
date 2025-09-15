
from django import views
from django.urls import include, path 
from .views import  home, about,   EventCreateView,  add_comment, event_detail, download_images
from django.urls import path
from django.urls import path
from . import views  # Import from current directory (core app)
from django.urls import path
from . import views
from django.urls import path
from .views import media_gallery
from .views import  like_verse
app_name = 'core'

urlpatterns = [
    path('',home, name='home'),
    path('about/',about, name='about'),
    path('media/', media_gallery, name='media_gallery'),
    path('contact/', views.contact_view, name='contact'),
    path('prayer-request/', views.prayer_request, name='prayer_request'),
    path('chatroom/', views.chatroom, name='chatroom'),
    path('create/', EventCreateView.as_view(), name='event_create'),
    path('<int:pk>/', event_detail, name='event_detail'),
    path('comment/<int:pk>/delete/', views.delete_comment, name='delete_comment'),
    path('<int:pk>/comment/', add_comment, name='add_comment'),
    path('download-images/', download_images, name='download_images'),
    path('api/event/<int:event_id>/like/', views.event_like, name='event_like'),
    path('api/event/<int:event_id>/likes/', views.event_likes_count, name='event_likes_count'),
    path('notifications/mark_as_read/<int:notification_id>/', views.mark_as_read, name='mark_as_read'),
     # Like functionality - accessible to everyone
    path('like/<int:verse_id>/', views.like_verse, name='like_verse'),
    
    # Share functionality - accessible to everyone  
    path('share/<int:verse_id>/', views.share_verse, name='share_verse'),
    
    # Get verse statistics - accessible to everyone
    path('stats/<int:verse_id>/', views.get_verse_stats, name='verse_stats'),

    path('api/online-users/exact/', views.exact_online_users, name='exact_online_users'),
    path('api/connection/heartbeat/', views.connection_heartbeat, name='connection_heartbeat'),
    

]
    
   
