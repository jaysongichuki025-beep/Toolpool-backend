"""
═══════════════════════════════════════════════════════════════════════════
apps/tools/urls.py — Router for Category + Tool ViewSets
═══════════════════════════════════════════════════════════════════════════
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, ToolViewSet

# DefaultRouter auto-generates:
#   GET/POST   /categories/
#   GET/PUT/PATCH/DELETE /categories/{slug}/
#   GET/POST   /tools/
#   GET/PUT/PATCH/DELETE /tools/{pk}/
#   plus @action routes like /tools/{pk}/status/
router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'tools', ToolViewSet, basename='tool')

urlpatterns = [
    path('', include(router.urls)),
]
