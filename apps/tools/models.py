"""
═══════════════════════════════════════════════════════════════════════════
apps/tools/models.py — Category, Tool, ToolImage schemas
═══════════════════════════════════════════════════════════════════════════
"""

from django.conf import settings
from django.db import models


class Category(models.Model):
    """
    Tool category (Gardening, Power Tools, etc.).
    SCHEMA 3 of 6 — managed by admins.
    """

    name = models.CharField(max_length=80, unique=True)
    # slug = URL-friendly version of name (e.g. "Power Tools" -> "power-tools")
    slug = models.SlugField(max_length=80, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        # Default order when we query Category.objects.all()
        verbose_name_plural = 'categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Tool(models.Model):
    """
    A tool listed by a lender for neighbors to borrow/rent.
    SCHEMA 4 of 6 — the core item of ToolPool.
    """

    class Condition(models.TextChoices):
        NEW = 'new', 'New'
        GOOD = 'good', 'Good'
        FAIR = 'fair', 'Fair'
        WORN = 'worn', 'Worn'

    class Status(models.TextChoices):
        # Status toggle from the MVP: Available / In Use / Under Maintenance
        AVAILABLE = 'available', 'Available'
        IN_USE = 'in_use', 'In Use'
        MAINTENANCE = 'maintenance', 'Under Maintenance'

    # Owner = the lender who listed this tool
    # settings.AUTH_USER_MODEL points at our custom users.User
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tools',  # user.tools.all()
    )
    # Category is required so we can filter browse results
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,  # PROTECT = cannot delete category if tools use it
        related_name='tools',
    )
    title = models.CharField(max_length=150)
    description = models.TextField()
    condition = models.CharField(
        max_length=20,
        choices=Condition.choices,
        default=Condition.GOOD,
    )
    # daily_fee = 0 means "free to borrow"
    daily_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.AVAILABLE,
    )
    pickup_instructions = models.TextField(
        blank=True,
        help_text='e.g. "Leave on porch after 5pm. Ring doorbell."',
    )
    neighborhood = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # updates on every save

    class Meta:
        ordering = ['-created_at']  # newest first

    def __str__(self):
        return self.title


class ToolImage(models.Model):
    """
    Photo attached to a tool.
    SCHEMA 5 of 6 — separate table so one tool can have many photos.
    """

    tool = models.ForeignKey(
        Tool,
        on_delete=models.CASCADE,
        related_name='images',  # tool.images.all()
    )
    # ImageField stores the file on disk (MEDIA_ROOT) and the path in the DB
    image = models.ImageField(upload_to='tools/%Y/%m/')  # folder by year/month
    is_primary = models.BooleanField(
        default=False,
        help_text='Show this photo first in browse results',
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Image for {self.tool.title}'
