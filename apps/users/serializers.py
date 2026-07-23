"""
═══════════════════════════════════════════════════════════════════════════
apps/users/serializers.py — Convert User/Profile <-> JSON
═══════════════════════════════════════════════════════════════════════════
WHY serializers?
  The database stores Python objects. The frontend speaks JSON.
  Serializers are the translator in both directions (read + write).
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import Profile

User = get_user_model()  # returns our custom users.User model


class ProfileSerializer(serializers.ModelSerializer):
    """Nested inside User responses so the frontend gets name + neighborhood."""

    class Meta:
        model = Profile
        fields = ('full_name', 'neighborhood', 'phone', 'bio')


class UserSerializer(serializers.ModelSerializer):
    """Public representation of the logged-in user (no password!)."""

    # nest profile as a read-only object inside the user JSON
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'role', 'created_at', 'profile')
        read_only_fields = ('id', 'created_at')


class RegisterSerializer(serializers.ModelSerializer):
    """
    Handles POST /api/auth/register/
    Accepts email, password, optional full_name / neighborhood / role.
    """

    # write_only = password is accepted on input but NEVER returned in JSON
    password = serializers.CharField(write_only=True, min_length=8)
    full_name = serializers.CharField(required=False, allow_blank=True, write_only=True)
    neighborhood = serializers.CharField(required=False, allow_blank=True, write_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'role', 'full_name', 'neighborhood')
        read_only_fields = ('id',)

    def validate_password(self, value):
        # Use Django's built-in password strength rules
        validate_password(value)
        return value

    def create(self, validated_data):
        # Pop profile fields before creating User (User model doesn't have them)
        full_name = validated_data.pop('full_name', '')
        neighborhood = validated_data.pop('neighborhood', '')
        password = validated_data.pop('password')

        user = User.objects.create_user(password=password, **validated_data)

        # Profile was auto-created by the post_save signal — now fill it in
        profile = user.profile
        profile.full_name = full_name
        profile.neighborhood = neighborhood
        profile.save()

        return user


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """PATCH /api/auth/me/ — update profile fields."""

    class Meta:
        model = Profile
        fields = ('full_name', 'neighborhood', 'phone', 'bio')
