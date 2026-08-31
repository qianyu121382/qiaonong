import uuid

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from .models import Category, Product, ProductImage


class CategoryChildSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "slug", "description", "banner", "sort_order")


class PublicCategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = (
            "id",
            "name",
            "slug",
            "description",
            "banner",
            "sort_order",
            "children",
        )

    def get_children(self, category):
        children = category.children.filter(is_active=True).order_by("sort_order", "id")
        return CategoryChildSerializer(children, many=True, context=self.context).data


class PublicProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ("id", "image", "alt_text", "sort_order")


class AdminProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ("id", "product", "image", "alt_text", "sort_order", "created_at")
        read_only_fields = ("id", "created_at")


class PublicProductListSerializer(serializers.ModelSerializer):
    category = CategoryChildSerializer(read_only=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "slug",
            "category",
            "tag",
            "summary",
            "specification",
            "cover",
            "hover_image",
            "sort_order",
            "is_featured",
        )


class PublicProductDetailSerializer(PublicProductListSerializer):
    images = PublicProductImageSerializer(many=True, read_only=True)

    class Meta(PublicProductListSerializer.Meta):
        fields = PublicProductListSerializer.Meta.fields + ("description", "images")


class AdminCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            "id",
            "name",
            "slug",
            "parent",
            "description",
            "banner",
            "sort_order",
            "is_active",
            "legacy_id",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "slug",
            "legacy_id",
            "created_at",
            "updated_at",
        )

    def create(self, validated_data):
        validated_data["slug"] = f"category-{uuid.uuid4().hex[:16]}"
        return super().create(validated_data)

    def validate(self, attrs):
        category = self.instance or Category()
        for field, value in attrs.items():
            setattr(category, field, value)
        try:
            category.clean()
        except DjangoValidationError as error:
            raise serializers.ValidationError(error.message_dict) from error
        if category.parent_id:
            attrs["banner"] = ""
        return attrs


class AdminProductSerializer(serializers.ModelSerializer):
    images = PublicProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "category",
            "name",
            "slug",
            "tag",
            "summary",
            "specification",
            "description",
            "cover",
            "hover_image",
            "sort_order",
            "is_featured",
            "is_active",
            "legacy_id",
            "images",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "slug", "legacy_id", "created_at", "updated_at")

    def create(self, validated_data):
        validated_data["slug"] = f"product-{uuid.uuid4().hex[:16]}"
        return super().create(validated_data)
