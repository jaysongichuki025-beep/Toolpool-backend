"""
═══════════════════════════════════════════════════════════════════════════
apps/users/models.py — User + Profile database schemas
═══════════════════════════════════════════════════════════════════════════
WHY two models?
  User  = login identity (email, password, role) — used by Django auth
  Profile = extra public info (name, neighborhood, phone) — 1-to-1 with User

This gives us TWO of the required 5+ database schemas.
═══════════════════════════════════════════════════════════════════════════
"""

# AbstractBaseUser = minimal user with password hashing, no username required
# PermissionsMixin = adds is_superuser / groups / permissions fields
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """
    Custom manager — Django needs this when we replace the default User model.
    WHY: default User uses username; we want email as the unique login field.
    """

    def create_user(self, email, password=None, **extra_fields):
        """Create a normal user (borrower/lender)."""
        if not email:
            raise ValueError('Users must have an email address')
        # normalize_email lowercases the domain part (Gmail.com -> gmail.com)
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        # set_password hashes the password — NEVER store plain text passwords
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create an admin user (can access /admin/ and admin APIs)."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', User.Role.ADMIN)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model.
    SCHEMA 1 of 6 — authentication identity.
    """

    class Role(models.TextChoices):
        """
        TextChoices = Django helper for fixed option lists.
        Stored in DB as the string value ('borrower', 'lender', 'admin').
        """
        BORROWER = 'borrower', 'Borrower'
        LENDER = 'lender', 'Lender'
        ADMIN = 'admin', 'Admin'

    # Email is unique and used to log in (instead of username)
    email = models.EmailField(unique=True)

    # Role controls what the user can do in the API
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.BORROWER,
        help_text='borrower | lender | admin',
    )

    # Django admin / staff flags
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # can log into /admin/

    # auto_now_add = set once when row is created
    created_at = models.DateTimeField(auto_now_add=True)

    # Tell Django which field is the "username" for login
    USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS asked by createsuperuser (besides USERNAME_FIELD + password)
    REQUIRED_FIELDS = []

    # Attach our custom manager
    objects = UserManager()

    def __str__(self):
        # Readable label in Django admin and shell
        return self.email


class Profile(models.Model):
    """
    Extra info about a user.
    SCHEMA 2 of 6 — one Profile per User (OneToOne).
    """

    # OneToOneField = each User has exactly one Profile
    # CASCADE = if User is deleted, delete their Profile too
    # related_name='profile' lets us do: user.profile
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    full_name = models.CharField(max_length=120, blank=True)
    # neighborhood used for "nearby tools" filtering (simple text, no GPS yet)
    neighborhood = models.CharField(max_length=120, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.full_name or self.user.email
