"""
URL configuration for optiview project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django default admin
    path('django-admin/', admin.site.urls),

    # Main app
    path('', include('app.urls')),

    # Custom admin panel
    path("admin-panel/", include("adminpanel.urls", namespace="adminpanel")),
  
    # Delivery panel
    path('delivery/', include('delivery.urls')),
]

# Serve media files during development only
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
