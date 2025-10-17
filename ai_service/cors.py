"""
Enhanced CORS configuration for ZRA Digital Fortress integration
"""
from django.conf import settings

class CORSMiddlewareConfig:
    """
    Custom CORS configuration for development and production
    """
    
    # Allowed origins for development
    DEVELOPMENT_ORIGINS = [
        "http://localhost:3000",      # Eric's React frontend
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://localhost:8080",      # Silas' Java backend
        "http://127.0.0.1:8080",
        "http://localhost:8081",
        "http://frontend:3000",       # Docker container names
        "http://backend:8080",
        "http://ai-service:8000",
    ]
    
    # Allowed methods
    ALLOWED_METHODS = [
        'GET',
        'POST',
        'PUT',
        'PATCH', 
        'DELETE',
        'OPTIONS'
    ]
    
    # Allowed headers
    ALLOWED_HEADERS = [
        'Content-Type',
        'Authorization',
        'X-Requested-With',
        'Accept',
        'Origin',
        'X-CSRFToken',
        'X-API-Key',
    ]
    
    @classmethod
    def get_allowed_origins(cls):
        """Get allowed origins based on environment"""
        if settings.DEBUG:
            return cls.DEVELOPMENT_ORIGINS
        else:
            # Production origins would be configured via environment variables
            production_origins = getattr(settings, 'CORS_ALLOWED_ORIGINS', [])
            return production_origins + cls.DEVELOPMENT_ORIGINS