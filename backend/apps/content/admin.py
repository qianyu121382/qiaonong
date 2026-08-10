from django.contrib import admin

from .models import ContentPage, HeroSlide, SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    list_display = ("title", "sort_order", "is_active", "updated_at")
    list_filter = ("is_active",)


@admin.register(ContentPage)
class ContentPageAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "sort_order", "is_active", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("title", "slug", "body")
