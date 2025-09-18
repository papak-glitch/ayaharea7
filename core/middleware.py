# middleware.py
from django.utils import timezone
from django.db import connection

class OnlineUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Create session BEFORE checking session_key
        if not request.session.session_key:
            request.session.create()
        
        # Only track page views, not admin/static files
        if (request.session.session_key and 
            not request.path.startswith('/admin/') and 
            not request.path.startswith('/static/') and
            not request.path.startswith('/media/') and
            not request.path.startswith('/__debug__/')):
            
            print("DEBUG: Tracking this session")
            
            try:
                session_key = request.session.session_key
                now = timezone.now()
                
                # Use raw SQL to avoid model issues
                with connection.cursor() as cursor:
                    # Create table if it doesn't exist
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS core_usersession (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            session_key VARCHAR(40) UNIQUE NOT NULL,
                            last_activity DATETIME NOT NULL,
                            user_id INTEGER NULL,
                            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    print("DEBUG: Table created/verified")
                    
                    # Insert or update session
                    cursor.execute("""
                        INSERT OR REPLACE INTO core_usersession 
                        (session_key, last_activity, user_id) 
                        VALUES (?, ?, ?)
                    """, [
                        session_key, 
                        now.strftime('%Y-%m-%d %H:%M:%S'), 
                        request.user.id if request.user.is_authenticated else None
                    ])
                    print(f"DEBUG: Session {session_key} updated")
                    
            except Exception as e:
                print(f"DEBUG: Middleware error: {e}")
        
        response = self.get_response(request)
        return response