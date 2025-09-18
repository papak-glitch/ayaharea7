# management/commands/clean_old_sessions.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from core.models import UserSession

class Command(BaseCommand):
    help = 'Clean up old user sessions'
    
    def handle(self, *args, **options):
        # Delete sessions inactive for more than 24 hours
        twenty_four_hours_ago = timezone.now() - timedelta(hours=24)
        deleted_count, _ = UserSession.objects.filter(
            last_activity__lt=twenty_four_hours_ago
        ).delete()
        
        self.stdout.write(f'Deleted {deleted_count} old sessions')