"""
═══════════════════════════════════════════════════════════════════════════
apps/tools/views.py — Category + Tool ViewSets
═══════════════════════════════════════════════════════════════════════════
WHY ViewSets?
  One class can handle list/create/retrieve/update/delete.
  A Router wires them to URLs automatically.
"""

from django.db.models import Q
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response

from apps.rentals.models import RentalRequest
from apps.users.permissions import IsAdminRole, IsOwnerOrReadOnly

from .models import Category, Tool, ToolImage
from .serializers import (
    CategorySerializer,
    ToolImageSerializer,
    ToolListSerializer,
    ToolSerializer,
    ToolStatusSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    /api/categories/
    GET = public (so browse works before login)
    POST/PUT/DELETE = admin only
    """

    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    lookup_field = 'slug'  # /api/categories/power-tools/ instead of numeric id
    search_fields = ('name', 'description')

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsAdminRole()]
        # AllowAny for list/retrieve — neighbors can browse categories without an account
        if self.action in ('list', 'retrieve'):
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        # Admins see inactive categories too
        if self.request.user.is_authenticated and (
            self.request.user.role == 'admin' or self.request.user.is_superuser
        ):
            return Category.objects.all()
        return Category.objects.filter(is_active=True)


class ToolViewSet(viewsets.ModelViewSet):
    """
    /api/tools/
    Browse, create, edit tools. Filter by category, search, neighborhood, status.
    """

    # MultiPartParser = needed for image uploads from forms
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filterset_fields = ('category', 'status', 'condition', 'neighborhood')
    search_fields = ('title', 'description', 'neighborhood')
    ordering_fields = ('daily_fee', 'created_at', 'title')

    def get_permissions(self):
        # Public browse + detail + availability calendar
        if self.action in ('list', 'retrieve', 'availability'):
            return [permissions.AllowAny()]
        # Create/edit/status/images require login (+ owner checks via IsOwnerOrReadOnly)
        return [permissions.IsAuthenticated(), IsOwnerOrReadOnly()]

    def get_queryset(self):
        qs = Tool.objects.select_related('category', 'owner').prefetch_related('images')
        # Optional: ?mine=1 → only tools owned by current user (lender dashboard)
        if self.request.query_params.get('mine') == '1':
            if not self.request.user.is_authenticated:
                return qs.none()
            return qs.filter(owner=self.request.user)
        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return ToolListSerializer
        if self.action == 'update_status':
            return ToolStatusSerializer
        return ToolSerializer

    def perform_create(self, serializer):
        # Force owner = logged-in user (never trust client-supplied owner id)
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['patch'], url_path='status')
    def update_status(self, request, pk=None):
        """
        PATCH /api/tools/{id}/status/
        Body: { "status": "available" | "in_use" | "maintenance" }
        Owner only — pauses requests when under maintenance.
        """
        tool = self.get_object()  # also runs IsOwnerOrReadOnly
        if tool.owner != request.user and not request.user.is_superuser:
            return Response({'detail': 'Only the owner can change status.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = ToolStatusSerializer(tool, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ToolSerializer(tool, context={'request': request}).data)

    @action(detail=True, methods=['get'], url_path='availability')
    def availability(self, request, pk=None):
        """
        GET /api/tools/{id}/availability/
        Returns date ranges already blocked by approved/active rentals.
        Frontend paints these on the calendar.
        """
        tool = self.get_object()
        blocked = (
            RentalRequest.objects.filter(tool=tool)
            .filter(Q(status=RentalRequest.Status.APPROVED) | Q(status=RentalRequest.Status.ACTIVE))
            .values('start_date', 'end_date', 'status')
        )
        return Response({
            'tool_id': tool.id,
            'tool_status': tool.status,
            'blocked_ranges': list(blocked),
        })

    @action(detail=True, methods=['post'], url_path='images')
    def add_image(self, request, pk=None):
        """POST /api/tools/{id}/images/ — upload an extra photo (owner only)."""
        tool = self.get_object()
        if tool.owner != request.user:
            return Response({'detail': 'Only the owner can add images.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = ToolImageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(tool=tool)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
