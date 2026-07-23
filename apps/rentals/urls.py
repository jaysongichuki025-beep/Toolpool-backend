"""URL routes for rentals + admin monitoring."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AdminRentalViewSet, DisputeViewSet, RentalRequestViewSet

router = DefaultRouter()
router.register(r'rentals', RentalRequestViewSet, basename='rental')
router.register(r'admin/rentals', AdminRentalViewSet, basename='admin-rental')
router.register(r'disputes', DisputeViewSet, basename='dispute')

urlpatterns = [
    path('', include(router.urls)),
]
