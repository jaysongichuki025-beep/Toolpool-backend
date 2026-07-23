"""Django admin for rentals."""

from django.contrib import admin

from .models import Dispute, RentalRequest


@admin.register(RentalRequest)
class RentalRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'tool', 'borrower', 'start_date', 'end_date', 'status', 'total_fee')
    list_filter = ('status',)
    search_fields = ('tool__title', 'borrower__email')


@admin.register(Dispute)
class DisputeAdmin(admin.ModelAdmin):
    list_display = ('id', 'rental', 'flagged_by', 'status', 'created_at')
    list_filter = ('status',)
