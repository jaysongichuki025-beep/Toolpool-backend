"""
═══════════════════════════════════════════════════════════════════════════
apps/users/permissions.py — Custom permission classes
═══════════════════════════════════════════════════════════════════════════
WHY custom permissions?
  DRF's built-in IsAdminUser checks is_staff.
  We also check our custom role field for ToolPool admin features.
"""

from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminRole(BasePermission):
    """Only users with role='admin' (or Django superusers) may proceed."""

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (user.role == 'admin' or user.is_superuser)
        )


class IsOwnerOrReadOnly(BasePermission):
    """
    Read (GET/HEAD/OPTIONS) = anyone authenticated.
    Write (PUT/PATCH/DELETE) = only the object owner.
    Used on Tool detail views.
    """

    def has_object_permission(self, request, view, obj):
        # SAFE_METHODS = GET, HEAD, OPTIONS (read-only)
        if request.method in SAFE_METHODS:
            return True
        # obj.owner for Tool; fall back to obj.user if present
        owner = getattr(obj, 'owner', None) or getattr(obj, 'user', None)
        return owner == request.user
