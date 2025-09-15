from django.utils import timezone
from .models import ActiveConnection, VisitorProfile
import uuid
from django.db import transaction

class ExactOnlineUsersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Skip tracking for certain paths
        if any(request.path.startswith(p) for p in ['/admin/', '/static/', '/media/', '/api/']):
            return self.get_response(request)
        
        # Generate or get visitor ID
        visitor_id = request.COOKIES.get('visitor_id')
        if not visitor_id:
            visitor_id = str(uuid.uuid4())
        
        response = self.get_response(request)
        
        # Set visitor ID cookie if not present (1 year expiration)
        if 'visitor_id' not in request.COOKIES:
            response.set_cookie('visitor_id', visitor_id, max_age=31536000)  # 1 year
        
        # Track connection after response
        self.track_connection(request, visitor_id)
        
        return response
    
    def track_connection(self, request, visitor_id):
        if not hasattr(request, 'session') or not request.session.session_key:
            return
        
        try:
            with transaction.atomic():
                # Get or create visitor profile
                visitor_profile, created = VisitorProfile.objects.get_or_create(
                    visitor_id=visitor_id,
                    defaults={
                        'user': request.user if request.user.is_authenticated else None,
                        'first_seen': timezone.now(),
                        'last_seen': timezone.now(),
                        'total_visits': 1
                    }
                )
                
                if not created:
                    visitor_profile.last_seen = timezone.now()
                    visitor_profile.total_visits += 1
                    if request.user.is_authenticated:
                        visitor_profile.user = request.user
                    visitor_profile.save()
                
                # Update or create active connection
                ActiveConnection.objects.update_or_create(
                    session_key=request.session.session_key,
                    defaults={
                        'user': request.user if request.user.is_authenticated else None,
                        'ip_address': self.get_client_ip(request),
                        'user_agent': request.META.get('HTTP_USER_AGENT', '')[:500],
                        'last_heartbeat': timezone.now(),
                        'is_active': True
                    }
                )
                
        except Exception as e:
            # Log error but don't break the request
            print(f"Error tracking connection: {e}")
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip