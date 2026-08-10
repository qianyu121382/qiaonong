from rest_framework import serializers

from .models import ContentPage, HeroSlide, SiteSettings


class SiteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSettings
        fields = (
            "site_name",
            "logo",
            "home_title",
            "home_subtitle",
            "home_intro_title",
            "home_intro_body",
            "home_intro_image",
            "company_name",
            "phone",
            "email",
            "address",
            "social_qr",
            "footer_text",
            "icp_number",
            "icp_url",
            "updated_at",
        )
        read_only_fields = ("updated_at",)


class HeroSlideSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeroSlide
        fields = (
            "id",
            "title",
            "subtitle",
            "image",
            "link_url",
            "sort_order",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class ContentPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentPage
        fields = (
            "id",
            "slug",
            "title",
            "summary",
            "body",
            "image",
            "sort_order",
            "is_active",
            "legacy_id",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")
