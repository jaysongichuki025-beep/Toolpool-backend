"""
═══════════════════════════════════════════════════════════════════════════
apps/users/urls.py — Auth URL routes
═══════════════════════════════════════════════════════════════════════════
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import EmailTokenObtainPairView, MeView, RegisterView

# WHY app_name? Lets us reverse URLs like: reverse('users:login')
app_name = 'users'

urlpatterns = [
    # Create account
    path('register/', RegisterView.as_view(), name='register'),
    # Login → JWT access + refresh tokens
    path('login/', EmailTokenObtainPairView.as_view(), name='login'),
    # Exchange refresh token for a new access token
    path('refresh/', TokenRefreshView.as_view(), name='refresh'),
    # Current logged-in user
    path('me/', MeView.as_view(), name='me'),
]
