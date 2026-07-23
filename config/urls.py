"""
═══════════════════════════════════════════════════════════════════════════
config/urls.py — Root URL router
═══════════════════════════════════════════════════════════════════════════
WHY: Every incoming HTTP path starts here, then is forwarded to an app.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Django admin panel (create categories, inspect users, etc.)
    path('admin/', admin.site.urls),

    # Auth endpoints: /api/auth/register/, /api/auth/login/, ...
    path('api/auth/', include('apps.users.urls')),

    # Categories + Tools
    path('api/', include('apps.tools.urls')),

    # Rentals + Disputes + Admin rental log
    path('api/', include('apps.rentals.urls')),
]

# In DEBUG mode, Django itself serves uploaded media files.
# In production, Nginx or cloud storage should serve MEDIA_ROOT.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
