import logging
import re
from datetime import datetime, time
from django.http import HttpResponseForbidden
from django.utils import timezone

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware:
    """
    Middleware to log all requests with their path, method, and timestamp.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log the request details
        logger.info(
            f"Request: {request.method} {request.path} at {timezone.now().isoformat()}"
        )
        
        # Process the request
        response = self.get_response(request)
        
        # Return the response
        return response


class RestrictAccessByTimeMiddleware:
    """
    Middleware to restrict access to the application during certain hours.
    By default, restricts access between 11 PM and 6 AM.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # Default restricted hours: 11 PM to 6 AM
        self.restricted_start = time(23, 0)  # 11 PM
        self.restricted_end = time(6, 0)     # 6 AM

    def __call__(self, request):
        # Skip restriction for admin paths
        if request.path.startswith('/admin/'):
            return self.get_response(request)
            
        # Get current time
        current_time = timezone.now().time()
        
        # Check if current time is within restricted hours
        is_restricted = False
        if self.restricted_start < self.restricted_end:
            # Simple case: restricted period doesn't cross midnight
            is_restricted = self.restricted_start <= current_time <= self.restricted_end
        else:
            # Complex case: restricted period crosses midnight
            is_restricted = current_time >= self.restricted_start or current_time <= self.restricted_end
        
        if is_restricted:
            return HttpResponseForbidden(
                "The messaging service is not available during these hours. "
                "Please try again between 6 AM and 11 PM."
            )
            
        return self.get_response(request)


class OffensiveLanguageMiddleware:
    """
    Middleware to detect and block messages containing offensive language.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # Simple list of offensive words to filter
        self.offensive_patterns = [
            r'\b(badword1|badword2|badword3)\b',  # Replace with actual offensive words
            # Add more patterns as needed
        ]
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.offensive_patterns]

    def __call__(self, request):
        # Only check POST requests that might contain message content
        if request.method == 'POST' and 'message_body' in request.POST:
            message = request.POST.get('message_body', '')
            
            # Check for offensive content
            for pattern in self.compiled_patterns:
                if pattern.search(message):
                    return HttpResponseForbidden(
                        "Your message contains language that violates our community guidelines."
                    )
        
        return self.get_response(request)