"""
═══════════════════════════════════════════════════════════════════════════
apps/users/views.py — Auth API endpoints (register, me, profile update)
═══════════════════════════════════════════════════════════════════════════
"""

from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (
    ProfileUpdateSerializer,
    RegisterSerializer,
    UserSerializer,
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """
    POST /api/auth/register/
    Public — anyone can create an account.
    Returns the new user JSON (no tokens — client then calls login).
    """

    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    # AllowAny overrides the global IsAuthenticated default in settings
    permission_classes = [permissions.AllowAny]


class MeView(APIView):
    """
    GET  /api/auth/me/  → current user + profile
    PATCH /api/auth/me/ → update profile fields
    Requires a valid JWT access token.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # request.user is set by JWTAuthentication from the Bearer token
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        profile = request.user.profile
        serializer = ProfileUpdateSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # Return the full user object so the frontend stays in sync
        return Response(UserSerializer(request.user).data)


class EmailTokenObtainPairView(TokenObtainPairView):
    """
    POST /api/auth/login/
    Body: { "email": "...", "password": "..." }
    Returns: { "access": "...", "refresh": "..." }

    SimpleJWT's default expects "username". Our USERNAME_FIELD is "email",
    so the default TokenObtainPairView already works with email if the
    client sends {"email": ..., "password": ...}.
    We keep this subclass so the URL name is clear for beginners.
    """

    permission_classes = [permissions.AllowAny]
