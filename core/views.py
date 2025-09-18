from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView
from .models import  Event, GalleryImage
from .forms import EventForm
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import Event, Comment, Leader
from .forms import CommentForm, ReplyForm
from django.http import HttpResponse, Http404
from .models import MediaImage
import zipfile
import io
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db import transaction

def get_client_ip(request):
    """Get the client IP address from the request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def home(request):  # Renamed from verse_of_the_day to match your URL pattern
    """Main home view that displays everything"""
    print("DEBUG: Home view called")
    
    # Get the most recent verse
    verse = BibleVerse.objects.order_by('-date').first()
    
    print(f"DEBUG: Found verse: {verse}")
    
    if not verse:
        # Create a default verse if none exists
        print("DEBUG: No verse found, creating default")
        verse = BibleVerse.objects.create(
            reference="John 3:16",
            text="For God so loved the world that he gave his one and only Son, that whoever believes in him shall not perish but have eternal life.",
            like_count=0,
            share_count=0
        )
    
    # Get counts for the current user
    user_liked = False
    user_shared = False
    
    # Ensure session exists
    if not request.session.session_key:
        request.session.create()
        request.session.save()
    
    interaction = VerseInteraction.objects.filter(
        verse=verse,
        session_key=request.session.session_key
    ).first()
    
    if interaction:
        user_liked = interaction.liked
        user_shared = interaction.shared
    
    # Get other data your template needs
    upcoming_events = Event.objects.filter(date__gte=timezone.now().date()).order_by('date')[:4]
    recent_events = Event.objects.filter(date__lt=timezone.now().date()).order_by('-date')[:4]
    
    context = {
        'verse': verse,
        'user_liked': user_liked,
        'user_shared': user_shared,
        'upcoming_events': upcoming_events,
        'recent_events': recent_events,
        # Add other context variables your template needs
    }
    
    return render(request, 'home.html', context)  # Make sure this matches your template name








def about(request):
    template_name = 'about.html'
    return render(request, template_name)

from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings

def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Prepare email content
        email_subject = f"New Contact Form Submission: {subject}"
        email_body = f"""
        Name: {name}
        Email: {email}
        Subject: {subject}
        
        Message:
        {message}
        """
        
        try:
            # Send email
            send_mail(
                email_subject,
                email_body,
                settings.DEFAULT_FROM_EMAIL,
                ['chiketadiwak@gmail.com'],  # Your Gmail address
                fail_silently=False,
            )
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('core:contact')  # Assuming 'contact' is your URL name
        except Exception as e:
            messages.error(request, f'There was an error sending your message: {str(e)}')
            return redirect('contact')
    
    return render(request, 'contact.html')


def prayer_request(request):
    if request.method == 'POST':
        prayer_name = request.POST.get('prayer_name', 'Anonymous')
        prayer_request = request.POST.get('prayer_request')
        is_private = request.POST.get('prayer_private', False)
        
        # Prepare email content
        subject = "New Prayer Request"
        message = f"""
        Name: {prayer_name}
        Private: {'Yes' if is_private else 'No'}
        
        Prayer Request:
        {prayer_request}
        """
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                ['chiketadiwak@gmail.com'],  # Your Gmail
                fail_silently=False,
            )
            messages.success(request, 'Your prayer request has been submitted. We will pray for you!')
        except Exception as e:
            messages.error(request, f'There was an error submitting your prayer request: {str(e)}')
        
        return redirect('core:contact')  # Redirect back to contact page
    
    return redirect('core:contact')  # In case of GET request

def chatroom(request):
    template_name = 'chatroom.html'
    return render(request, template_name)

def media(request):
    template_name = 'media.html'
    return render(request, template_name)

# events/views.py


class EventCreateView(CreateView):
    model = Event
    form_class = EventForm
    template_name = 'create.html'
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Event created successfully!')
        return response

    def get_success_url(self):
        return reverse('core:home')  # Assuming 'home' is the name of your homepage URL

 # events/views.py
from django.views.generic import DetailView
from .models import Event
# views.py
from django.shortcuts import render
from .models import MediaImage
from django.shortcuts import render
from .models import MediaAlbum

from django.core.paginator import Paginator

def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    comments_list = event.comments.filter(parent__isnull=True).order_by('-created_at')  # Get top-level comments only
    
    # Paginate with 5 comments per page
    paginator = Paginator(comments_list, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Check if we're loading replies for a specific comment
    load_replies_for = request.GET.get('show_replies')

    comment_form = CommentForm()
    reply_form = ReplyForm()

    # Check if "show all" was requested
    show_all = request.GET.get('show') == 'all'
    
    if show_all:
        # Show all comments without pagination
        return render(request, 'details.html', {
            'event': event,
            'comments': comments_list,
            'load_replies_for': load_replies_for,
            'comment_form': comment_form,
            'reply_form': reply_form,
            'show_all': False
        })
    

    
    if request.method == 'POST':
        # Get or set the commenter's name in session
        if 'author_name' in request.POST:
            request.session['commenter_name'] = request.POST.get('author_name')
            name = request.POST.get('author_name')
        else:
            name = request.session.get('commenter_name', 'Anonymous')
        
        # Create the reply
        parent_id = request.POST.get('parent_id')
        text = request.POST.get('text')
        parent_comment = get_object_or_404(Comment, id=parent_id)
        
        Comment.objects.create(
            event=parent_comment.event,
            author_name=name,
            text=text,
            parent=parent_comment
        )
    
        return redirect('core:event_detail', pk=event.pk)
    
    return render(request, 'details.html', {
        'event': event,
        'comments': page_obj,
        'load_replies_for': load_replies_for,
        'comment_form': comment_form,
        'reply_form': reply_form,
        'show_all': False
    })

  

def add_comment(request, pk):
    if request.method == 'POST':
        # Get or set the commenter's name in session
        if 'author_name' in request.POST:
            request.session['commenter_name'] = request.POST.get('author_name')
            name = request.POST.get('author_name')
        else:
            name = request.session.get('commenter_name', 'Anonymous')
        
        # Create the comment
        text = request.POST.get('text')
        event = get_object_or_404(Event, pk=pk)
        Comment.objects.create(
            event=event,
            author_name=name,
            text=text
        )

    return redirect('core:event_detail', pk=event.pk)

from django.contrib.auth.decorators import login_required

@require_POST

@require_POST
def delete_comment(request, pk):
    try:
        comment = get_object_or_404(Comment, pk=pk)
        event_id = comment.event.id  # Get the event ID before deletion
        
        # Check permissions
        if request.user.is_authenticated:
            if not (request.user.is_staff or comment.author_name == request.user.username):
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'error': 'Permission denied'}, status=403)
                return redirect('event_detail', pk=event_id)
        else:
            if comment.author_name != request.session.get('commenter_name'):
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'error': 'Permission denied'}, status=403)
                return redirect('core:event_detail', pk=event_id)

        comment.delete()
        
        # Handle AJAX requests
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'redirect_url': reverse('core:event_detail', kwargs={'pk': event_id})})
        
        # Handle regular form submission
        return redirect('core:event_detail', pk=event_id)

    except Comment.DoesNotExist:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Comment not found'}, status=404)
        return redirect('core:event_detail', pk=event_id)
    except Exception as e:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': str(e)}, status=500)
        return redirect('core:event_detail', pk=event_id)


# views.py
def about(request):
    leaders = Leader.objects.filter(is_active=True).order_by('order')
    values = [
        {
            'title': 'Biblical Foundation',
            'description': 'We base everything we do on God\'s Word'
        },
        {
            'title': 'Authentic Community',
            'description': 'Building real relationships centered on Christ'
        },
        # Add more values
    ]
    return render(request, 'about.html', {
        'leaders': leaders,
        'values': values
    })





def media_gallery(request):
    recent_albums = MediaAlbum.objects.filter(is_recent=True).prefetch_related('images').order_by('-date_taken')
    archive_albums = MediaAlbum.objects.filter(is_recent=False).prefetch_related('images').order_by('-date_taken')
    all_albums = MediaAlbum.objects.all().order_by('-date_taken')

    
    return render(request, 'media.html', {
        'recent_albums': recent_albums,
        'archive_albums': archive_albums,
        'all_albums': all_albums,
    })

def download_images(request):
    image_ids = request.POST.getlist('image_ids')
    images = MediaImage.objects.filter(id__in=image_ids, album__is_public=True)
    
    if not images.exists():
        raise Http404("No images found")
    
    # Create a zip file in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for image in images:
            zip_file.write(image.image.path, image.image.name.split('/')[-1])
    
    # Prepare response
    response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="selected_images.zip"'
    return response

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
import json
from .models import Event, EventLike

@csrf_exempt
@require_http_methods(["POST"])
def event_like(request, event_id):
    """Handle like/dislike actions for events"""
    try:
        event = get_object_or_404(Event, id=event_id)
        data = json.loads(request.body)
        
        device_id = data.get('device_id')
        action = data.get('action')  # 'like' or 'dislike'
        is_adding = data.get('is_adding', True)
        
        if not device_id or action not in ['like', 'dislike']:
            return JsonResponse({'error': 'Invalid data'}, status=400)
        
        # Get or create the reaction record
        reaction, created = EventLike.objects.get_or_create(
            event=event,
            device_id=device_id,
            defaults={'reaction': action}
        )
        
        if not created:
            if is_adding:
                # Update existing reaction
                reaction.reaction = action
                reaction.save()
            else:
                # Remove reaction
                reaction.delete()
        
        # Get updated counts
        counts = event.reactions.aggregate(
            likes=Count('id', filter=Q(reaction='like')),
            dislikes=Count('id', filter=Q(reaction='dislike'))
        )
        
        return JsonResponse({
            'success': True,
            'likes': counts['likes'] or 0,
            'dislikes': counts['dislikes'] or 0
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def event_likes_count(request, event_id):
    """Get current like/dislike counts for an event"""
    try:
        event = get_object_or_404(Event, id=event_id)
        
        counts = event.reactions.aggregate(
            likes=Count('id', filter=Q(reaction='like')),
            dislikes=Count('id', filter=Q(reaction='dislike'))
        )
        
        return JsonResponse({
            'likes': counts['likes'] or 0,
            'dislikes': counts['dislikes'] or 0
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    


from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from .models import BibleVerse, VerseInteraction
import json
import os

def verse_of_the_day(request):
    """Main view that displays the verse of the day"""
    print("DEBUG: verse_of_the_day view called")
    
    # Get the most recent verse
    verse = BibleVerse.objects.order_by('-date').first()
    
    print(f"DEBUG: Found verse: {verse}")
    
    if not verse:
        # Create a default verse if none exists
        print("DEBUG: No verse found, creating default")
        verse = BibleVerse.objects.create(
            reference="John 3:16",
            text="For God so loved the world that he gave his one and only Son, that whoever believes in him shall not perish but have eternal life.",
            like_count=0,
            share_count=0
        )
    
    # Get counts for the current user
    user_liked = False
    user_shared = False
    
    # Ensure session exists
    if not request.session.session_key:
        request.session.create()
        request.session.save()
    
    interaction = VerseInteraction.objects.filter(
        verse=verse,
        session_key=request.session.session_key
    ).first()
    
    if interaction:
        user_liked = interaction.liked
        user_shared = interaction.shared
    
    # Debug: Check template existence
    template_path = os.path.join(settings.BASE_DIR, 'templates', 'verse_display.html')
    print(f"DEBUG: Looking for template at: {template_path}")
    print(f"DEBUG: Template exists: {os.path.exists(template_path)}")
    
    context = {
        'verse': verse,
        'user_liked': user_liked,
        'user_shared': user_shared,
    }
    
    return render(request, 'verse_display.html', context)

@csrf_exempt
@require_POST
def like_verse(request):
    try:
        # Ensure session exists
        if not request.session.session_key:
            request.session.create()
            request.session.save()
        
        data = json.loads(request.body)
        reference = data.get('reference', '')
        text = data.get('text', '')
        
        if not reference:
            return JsonResponse({'success': False, 'error': 'No reference provided'})
        
        # Get or create verse
        verse, created = BibleVerse.objects.get_or_create(
            reference=reference,
            defaults={'text': text}
        )
        
        # If verse exists but text is empty, update it
        if not created and not verse.text and text:
            verse.text = text
            verse.save()
        
        # Check if interaction already exists
        interaction = VerseInteraction.objects.filter(
            verse=verse,
            session_key=request.session.session_key
        ).first()
        
        if interaction:
            # Toggle like status
            interaction.liked = not interaction.liked
            interaction.save()
        else:
            # Create new interaction
            interaction = VerseInteraction.objects.create(
                verse=verse,
                session_key=request.session.session_key,
                liked=True
            )
        
        # Update counts
        verse.like_count = VerseInteraction.objects.filter(verse=verse, liked=True).count()
        verse.share_count = VerseInteraction.objects.filter(verse=verse, shared=True).count()
        verse.save()
        
        return JsonResponse({
            'success': True,
            'liked': interaction.liked,
            'like_count': verse.like_count,
            'share_count': verse.share_count
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@require_POST
def share_verse(request):
    try:
        # Ensure session exists
        if not request.session.session_key:
            request.session.create()
            request.session.save()
        
        data = json.loads(request.body)
        reference = data.get('reference', '')
        text = data.get('text', '')
        
        if not reference:
            return JsonResponse({'success': False, 'error': 'No reference provided'})
        
        # Get or create verse
        verse, created = BibleVerse.objects.get_or_create(
            reference=reference,
            defaults={'text': text}
        )
        
        # If verse exists but text is empty, update it
        if not created and not verse.text and text:
            verse.text = text
            verse.save()
        
        # Check if interaction already exists
        interaction = VerseInteraction.objects.filter(
            verse=verse,
            session_key=request.session.session_key
        ).first()
        
        if interaction:
            # Update existing interaction
            interaction.shared = True
            interaction.save()
        else:
            # Create new interaction
            interaction = VerseInteraction.objects.create(
                verse=verse,
                session_key=request.session.session_key,
                shared=True
            )
        
        # Update counts
        verse.share_count = VerseInteraction.objects.filter(verse=verse, shared=True).count()
        verse.like_count = VerseInteraction.objects.filter(verse=verse, liked=True).count()
        verse.save()
        
        return JsonResponse({
            'success': True,
            'shared': True,
            'share_count': verse.share_count,
            'like_count': verse.like_count
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def get_verse_counts(request, reference):
    """Get like and share counts for a verse"""
    try:
        verse = BibleVerse.objects.get(reference=reference)
        user_liked = False
        user_shared = False
        
        if request.session.session_key:
            interaction = VerseInteraction.objects.filter(
                verse=verse,
                session_key=request.session.session_key
            ).first()
            
            if interaction:
                user_liked = interaction.liked
                user_shared = interaction.shared
        
        return JsonResponse({
            'success': True,
            'like_count': verse.like_count,
            'share_count': verse.share_count,
            'user_liked': user_liked,
            'user_shared': user_shared
        })
        
    except BibleVerse.DoesNotExist:
        return JsonResponse({
            'success': True,
            'like_count': 0,
            'share_count': 0,
            'user_liked': False,
            'user_shared': False
        })
    
# views.py - add this function
import random

def get_random_verse(request):
    """Get a random verse from the database"""
    verses = BibleVerse.objects.all()
    if verses.exists():
        random_verse = random.choice(verses)
        return JsonResponse({
            'success': True,
            'reference': random_verse.reference,
            'text': random_verse.text,
            'like_count': random_verse.like_count,
            'share_count': random_verse.share_count
        })
    else:
        return JsonResponse({
            'success': False,
            'error': 'No verses available'
        })    