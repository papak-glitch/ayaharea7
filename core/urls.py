
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
    
]
