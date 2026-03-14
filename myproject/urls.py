# myproject/urls.py

from django.contrib import admin
from django.urls import path, include 

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 1. API Interface: This path handles all API calls starting with '/api/'.
    # It must be defined explicitly.
    path('api/', include('myapp.urls')), 
    
    # 2. Web Interface: This path handles all standard HTML views (e.g., home, map, accounts).
    path('', include('myapp.urls')),
    
    # Standard authentication routes
    path('accounts/', include('django.contrib.auth.urls')), 
]