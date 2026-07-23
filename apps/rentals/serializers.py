"""
═══════════════════════════════════════════════════════════════════════════
apps/rentals/serializers.py
═══════════════════════════════════════════════════════════════════════════
"""

from decimal import Decimal

from rest_framework import serializers

from apps.tools.models import Tool

from .models import Dispute, RentalRequest


class RentalRequestSerializer(serializers.ModelSerializer):
    """Full rental request for create + detail views."""

    tool_title = serializers.CharField(source='tool.title', read_only=True)
    borrower_email = serializers.EmailField(source='borrower.email', read_only=True)
    owner_email = serializers.EmailField(source='tool.owner.email', read_only=True)

    class Meta:
        model = RentalRequest
        fields = (
            'id', 'tool', 'tool_title', 'borrower', 'borrower_email', 'owner_email',
            'start_date', 'end_date', 'status', 'total_fee', 'message',
            'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'borrower', 'status', 'total_fee', 'created_at', 'updated_at')

    def validate(self, attrs):
        """Cross-field validation — dates + tool availability."""
        start = attrs.get('start_date')
        end = attrs.get('end_date')
        tool = attrs.get('tool')

        if start and end and end < start:
            raise serializers.ValidationError({'end_date': 'End date must be on or after start date.'})

        if tool and tool.status != Tool.Status.AVAILABLE:
            raise serializers.ValidationError({'tool': f'Tool is currently "{tool.status}" and cannot be requested.'})

        # Block overlapping approved/active rentals
        if tool and start and end:
            overlap = RentalRequest.objects.filter(
                tool=tool,
                status__in=[RentalRequest.Status.APPROVED, RentalRequest.Status.ACTIVE, RentalRequest.Status.PENDING],
                start_date__lte=end,
                end_date__gte=start,
            )
            # When updating, exclude self
            if self.instance:
                overlap = overlap.exclude(pk=self.instance.pk)
            if overlap.exists():
                raise serializers.ValidationError(
                    {'start_date': 'Those dates overlap an existing request or rental.'}
                )

        return attrs

    def create(self, validated_data):
        tool = validated_data['tool']
        start = validated_data['start_date']
        end = validated_data['end_date']
        # Inclusive day count: Jan 1–Jan 1 = 1 day
        days = (end - start).days + 1
        validated_data['total_fee'] = (tool.daily_fee or Decimal('0')) * days
        # borrower set in the view via perform_create
        return super().create(validated_data)


class RentalRespondSerializer(serializers.Serializer):
    """
    PATCH /api/rentals/{id}/respond/
    Body: { "action": "approve" } or { "action": "decline" }
    """

    action = serializers.ChoiceField(choices=['approve', 'decline'])


class DisputeSerializer(serializers.ModelSerializer):
    rental_tool = serializers.CharField(source='rental.tool.title', read_only=True)

    class Meta:
        model = Dispute
        fields = (
            'id', 'rental', 'rental_tool', 'flagged_by', 'reason',
            'status', 'created_at',
        )
        read_only_fields = ('id', 'flagged_by', 'created_at')
