"""
═══════════════════════════════════════════════════════════════════════════
apps/tools/serializers.py
═══════════════════════════════════════════════════════════════════════════
"""

from rest_framework import serializers

from .models import Category, Tool, ToolImage


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'description', 'is_active')
        read_only_fields = ('id',)


class ToolImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ToolImage
        fields = ('id', 'image', 'is_primary', 'uploaded_at')
        read_only_fields = ('id', 'uploaded_at')


class ToolSerializer(serializers.ModelSerializer):
    """
    Full tool detail — used for retrieve / create / update.
    Nested images + category name for the frontend.
    """

    # Read nested images; write separately via ToolImage endpoint or multipart
    images = ToolImageSerializer(many=True, read_only=True)
    # Show category name alongside category id
    category_name = serializers.CharField(source='category.name', read_only=True)
    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    # Allow uploading one primary image when creating a tool (optional)
    primary_image = serializers.ImageField(write_only=True, required=False)

    class Meta:
        model = Tool
        fields = (
            'id', 'owner', 'owner_email', 'category', 'category_name',
            'title', 'description', 'condition', 'daily_fee', 'status',
            'pickup_instructions', 'neighborhood',
            'images', 'primary_image',
            'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'owner', 'created_at', 'updated_at')

    def create(self, validated_data):
        # Pull optional image out before creating Tool
        primary_image = validated_data.pop('primary_image', None)
        # Owner comes from the logged-in user (set in the view)
        tool = Tool.objects.create(**validated_data)
        if primary_image:
            ToolImage.objects.create(tool=tool, image=primary_image, is_primary=True)
        return tool

    def update(self, instance, validated_data):
        primary_image = validated_data.pop('primary_image', None)
        # Standard field updates
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if primary_image:
            # Mark old primary as non-primary, add new one
            instance.images.filter(is_primary=True).update(is_primary=False)
            ToolImage.objects.create(tool=instance, image=primary_image, is_primary=True)
        return instance


class ToolListSerializer(serializers.ModelSerializer):
    """Lighter serializer for browse grid (fewer fields = faster)."""

    category_name = serializers.CharField(source='category.name', read_only=True)
    primary_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Tool
        fields = (
            'id', 'title', 'category', 'category_name', 'daily_fee',
            'status', 'condition', 'neighborhood', 'primary_image_url',
            'created_at',
        )

    def get_primary_image_url(self, obj):
        # Prefer image marked primary; else first image
        img = obj.images.filter(is_primary=True).first() or obj.images.first()
        if not img:
            return None
        request = self.context.get('request')
        # build_absolute_uri → full URL the frontend can load
        return request.build_absolute_uri(img.image.url) if request else img.image.url


class ToolStatusSerializer(serializers.ModelSerializer):
    """PATCH status only — Available / In Use / Maintenance."""

    class Meta:
        model = Tool
        fields = ('status',)
