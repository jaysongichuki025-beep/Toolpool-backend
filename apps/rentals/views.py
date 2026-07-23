"""
═══════════════════════════════════════════════════════════════════════════
apps/rentals/views.py — Rental requests, owner respond, admin monitoring
═══════════════════════════════════════════════════════════════════════════
"""

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.users.permissions import IsAdminRole

from .models import Dispute, RentalRequest
from .serializers import (
    DisputeSerializer,
    RentalRespondSerializer,
    RentalRequestSerializer,
)


class RentalRequestViewSet(viewsets.ModelViewSet):
    """
    /api/rentals/
    Borrowers create requests. Owners see incoming ones. Admins see all.
    """

    serializer_class = RentalRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ('status', 'tool')
    ordering_fields = ('created_at', 'start_date')

    def get_queryset(self):
        user = self.request.user
        qs = RentalRequest.objects.select_related('tool', 'tool__owner', 'borrower')

        # Admin sees everything
        if user.role == 'admin' or user.is_superuser:
            return qs

        # ?as=borrower → my outgoing requests
        # ?as=owner    → requests on my tools
        # default      → both (union)
        perspective = self.request.query_params.get('as')
        if perspective == 'borrower':
            return qs.filter(borrower=user)
        if perspective == 'owner':
            return qs.filter(tool__owner=user)
        return qs.filter(borrower=user) | qs.filter(tool__owner=user)

    def perform_create(self, serializer):
        serializer.save(borrower=self.request.user)

    def destroy(self, request, *args, **kwargs):
        """Borrower can cancel only their own pending requests."""
        rental = self.get_object()
        if rental.borrower != request.user:
            return Response({'detail': 'Only the borrower can cancel.'}, status=status.HTTP_403_FORBIDDEN)
        if rental.status != RentalRequest.Status.PENDING:
            return Response({'detail': 'Only pending requests can be cancelled.'}, status=status.HTTP_400_BAD_REQUEST)
        rental.status = RentalRequest.Status.CANCELLED
        rental.save(update_fields=['status', 'updated_at'])
        return Response(RentalRequestSerializer(rental).data)

    @action(detail=True, methods=['patch'], url_path='respond')
    def respond(self, request, pk=None):
        """
        PATCH /api/rentals/{id}/respond/
        Owner accepts or declines a pending request.
        """
        rental = self.get_object()
        if rental.tool.owner != request.user and not request.user.is_superuser:
            return Response({'detail': 'Only the tool owner can respond.'}, status=status.HTTP_403_FORBIDDEN)
        if rental.status != RentalRequest.Status.PENDING:
            return Response({'detail': 'Only pending requests can be responded to.'}, status=status.HTTP_400_BAD_REQUEST)

        ser = RentalRespondSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        action_name = ser.validated_data['action']

        if action_name == 'approve':
            rental.status = RentalRequest.Status.APPROVED
            # Mark tool in use so others don't request it casually
            rental.tool.status = 'in_use'
            rental.tool.save(update_fields=['status', 'updated_at'])
        else:
            rental.status = RentalRequest.Status.DECLINED

        rental.save(update_fields=['status', 'updated_at'])
        return Response(RentalRequestSerializer(rental).data)

    @action(detail=True, methods=['patch'], url_path='mark-returned')
    def mark_returned(self, request, pk=None):
        """Owner marks tool as returned after the rental."""
        rental = self.get_object()
        if rental.tool.owner != request.user and not request.user.is_superuser:
            return Response({'detail': 'Only the tool owner can mark returned.'}, status=status.HTTP_403_FORBIDDEN)
        if rental.status not in (RentalRequest.Status.APPROVED, RentalRequest.Status.ACTIVE):
            return Response({'detail': 'Rental is not active.'}, status=status.HTTP_400_BAD_REQUEST)
        rental.status = RentalRequest.Status.RETURNED
        rental.save(update_fields=['status', 'updated_at'])
        rental.tool.status = 'available'
        rental.tool.save(update_fields=['status', 'updated_at'])
        return Response(RentalRequestSerializer(rental).data)


class AdminRentalViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/admin/rentals/ — full transaction log for admins.
    """

    queryset = RentalRequest.objects.select_related('tool', 'borrower', 'tool__owner').all()
    serializer_class = RentalRequestSerializer
    permission_classes = [IsAdminRole]
    filterset_fields = ('status',)


class DisputeViewSet(viewsets.ModelViewSet):
    """
    /api/disputes/ — flag and monitor rental problems.
    Create: authenticated users involved in the rental.
    List/update status: admin.
    """

    serializer_class = DisputeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ('status',)

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin' or user.is_superuser:
            return Dispute.objects.select_related('rental', 'flagged_by').all()
        return Dispute.objects.filter(flagged_by=user)

    def get_permissions(self):
        if self.action in ('update', 'partial_update', 'destroy'):
            return [IsAdminRole()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(flagged_by=self.request.user)
