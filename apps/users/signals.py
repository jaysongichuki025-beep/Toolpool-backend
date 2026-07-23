"""
═══════════════════════════════════════════════════════════════════════════
apps/users/signals.py — Auto-create a Profile when a User is created
═══════════════════════════════════════════════════════════════════════════
WHY signals?
  We don't want to remember to create Profile manually every time.
  post_save fires AFTER a User row is saved. If it was a new user (created=True),
  we create an empty Profile linked to them.
"""

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile_for_new_user(sender, instance, created, **kwargs):
    """
    sender   = the User model class
    instance = the actual User row that was just saved
    created  = True only on INSERT (new user), False on UPDATE
    """
    if created:
        Profile.objects.create(user=instance)
