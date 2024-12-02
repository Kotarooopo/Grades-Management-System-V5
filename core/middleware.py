from datetime import datetime, timedelta
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import logout

from typing import Any


class SessionTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        
        SESSION_TIMEOUT = timedelta(minutes=2)

        if request.user.is_authenticated:
            last_activity = request.session.get('last_activity')

            if last_activity:
                last_activity_time = datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S')

                if datetime.now() - last_activity_time > SESSION_TIMEOUT:
                    logout(request)
                    return redirect(reverse('login'))
                
            request.session['last_activity'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        response = self.get_response(request)
        return response