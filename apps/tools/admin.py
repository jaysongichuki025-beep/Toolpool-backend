"""Django admin registrations for tools app."""

from django.contrib import admin

from .models import Category, Tool, ToolImage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active')
    prepopulated_fields = {'slug': ('name',)}  # auto-fill slug from name in admin
    search_fields = ('name',)


class ToolImageInline(admin.TabularInline):
    model = ToolImage
    extra = 1


@admin.register(Tool)
class ToolAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'category', 'daily_fee', 'status', 'neighborhood')
    list_filter = ('status', 'category', 'condition')
    search_fields = ('title', 'description', 'owner__email')
    inlines = [ToolImageInline]


@admin.register(ToolImage)
class ToolImageAdmin(admin.ModelAdmin):
    list_display = ('tool', 'is_primary', 'uploaded_at')
