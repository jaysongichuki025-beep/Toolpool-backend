"""
apps/tools/views.py — Category + Tool ViewSets
"""

from django.db.models import Q
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response

from apps.rentals.models import RentalRequest
from apps.users.permissions import IsAdminRole, IsOwnerOrReadOnly

from .models import Category, Tool
from .serializers import (
    CategorySerializer,
    ToolImageSerializer,
    ToolListSerializer,
    ToolSerializer,
    ToolStatusSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    search_fields = ('name', 'description')

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsAdminRole()]
        if self.action in ('list', 'retrieve'):
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        if self.request.user.is_authenticated and (
            self.request.user.role == 'admin' or self.request.user.is_superuser
        ):
            return Category.objects.all()
        return Category.objects.filter(is_active=True)


class ToolViewSet(viewsets.ModelViewSet):
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filterset_fields = ('category', 'status', 'condition', 'neighborhood')
    search_fields = ('title', 'description', 'neighborhood')
    ordering_fields = ('daily_fee', 'created_at', 'title')

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'availability'):
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsOwnerOrReadOnly()]

    def get_queryset(self):
        qs = Tool.objects.select_related('category', 'owner').prefetch_related('images')
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
        serializer.save(owner=self.request.user)

    def destroy(self, request, *args, **kwargs):
        """DELETE /api/tools/{id}/ — Allows owners to delist their tool."""
        tool = self.get_object()
        tool.delete()
        return Response({'detail': 'Tool delisted successfully.'}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['patch'], url_path='status')
    def update_status(self, request, pk=None):
        tool = self.get_object()
        if tool.owner != request.user and not request.user.is_superuser:
            return Response({'detail': 'Only the owner can change status.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = ToolStatusSerializer(tool, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ToolSerializer(tool, context={'request': request}).data)

    @action(detail=True, methods=['get'], url_path='availability')
    def availability(self, request, pk=None):
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