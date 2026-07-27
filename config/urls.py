"""
═══════════════════════════════════════════════════════════════════════════
config/urls.py — Root URL router
═══════════════════════════════════════════════════════════════════════════
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Django admin panel
    path('admin/', admin.site.urls),

    # Auth endpoints: /api/auth/register/, /api/auth/login/, ...
    path('api/auth/', include('apps.users.urls')),

    # Categories + Tools
    path('api/', include('apps.tools.urls')),

    # Rentals + Disputes + Admin rental log
    path('api/', include('apps.rentals.urls')),
]

# Allow Django to serve uploaded media files in production/Render testing
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)