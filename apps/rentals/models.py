"""
═══════════════════════════════════════════════════════════════════════════
apps/rentals/models.py — RentalRequest + Dispute schemas
═══════════════════════════════════════════════════════════════════════════
"""

from django.conf import settings
from django.db import models

from apps.tools.models import Tool


class RentalRequest(models.Model):
    """
    A borrower's request to rent a tool for a date range.
    SCHEMA 6 of 6 — the transaction/order of ToolPool.
    """

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'       # waiting for owner
        APPROVED = 'approved', 'Approved'     # owner accepted
        DECLINED = 'declined', 'Declined'     # owner rejected
        ACTIVE = 'active', 'Active'           # currently borrowed
        RETURNED = 'returned', 'Returned'     # tool given back
        CANCELLED = 'cancelled', 'Cancelled'  # borrower cancelled

    tool = models.ForeignKey(
        Tool,
        on_delete=models.CASCADE,
        related_name='rental_requests',
    )
    borrower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='rental_requests',
    )
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    # total_fee = daily_fee * number of days (computed when request is created)
    total_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    message = models.TextField(blank=True)  # note from borrower to owner
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.tool.title} → {self.borrower.email} ({self.status})'


class Dispute(models.Model):
    """
    Flagged problem on a rental (damage, late return, etc.).
    Extra schema for admin transaction monitoring.
    """

    class Status(models.TextChoices):
        OPEN = 'open', 'Open'
        RESOLVED = 'resolved', 'Resolved'

    rental = models.OneToOneField(
        RentalRequest,
        on_delete=models.CASCADE,
        related_name='dispute',
    )
    flagged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='disputes_flagged',
    )
    reason = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Dispute on rental #{self.rental_id} ({self.status})'
