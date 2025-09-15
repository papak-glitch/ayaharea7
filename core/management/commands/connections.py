from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from core.models import ActiveConnection

class Command(BaseCommand):
    help = 'Clean up inactive connections'
    
    def handle(self, *args, **options):
        # Deactivate connections older than 5 minutes
        cutoff = timezone.now() - timedelta(minutes=5)
        
        deactivated_count = ActiveConnection.objects.filter(
            last_heartbeat__lt=cutoff,
            is_active=True
        ).update(is_active=False)
        
        # Permanently delete very old records (older than 24 hours)
        delete_cutoff = timezone.now() - timedelta(hours=24)
        deleted_count, _ = ActiveConnection.objects.filter(
            last_heartbeat__lt=delete_cutoff
        ).delete()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Deactivated {deactivated_count} stale connections, '
                f'deleted {deleted_count} old records'
            )
        )