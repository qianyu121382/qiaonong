from django.db.models import Q
from rest_framework import viewsets
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny, IsAdminUser

from .models import Category, Product, ProductImage
from .serializers import (
    AdminCategorySerializer,
    AdminProductImageSerializer,
    AdminProductSerializer,
    PublicCategorySerializer,
    PublicProductDetailSerializer,
    PublicProductListSerializer,
)


class PublicCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = PublicCategorySerializer
    lookup_field = "slug"

    def get_queryset(self):
        queryset = Category.objects.filter(is_active=True).prefetch_related("children")
        if self.action == "list":
            queryset = queryset.filter(parent__isnull=True)
        else:
            queryset = queryset.filter(
                Q(parent__isnull=True) | Q(parent__is_active=True)
            )
        return queryset.order_by("sort_order", "id")


class PublicProductViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = []
    permission_classes = [AllowAny]
    lookup_field = "slug"

    def get_serializer_class(self):
        if self.action == "retrieve":
            return PublicProductDetailSerializer
        return PublicProductListSerializer

    def get_queryset(self):
        queryset = (
            Product.objects.filter(is_active=True, category__is_active=True)
            .filter(Q(category__parent__isnull=True) | Q(category__parent__is_active=True))
            .select_related("category")
            .prefetch_related("images")
        )

        category_slug = self.request.query_params.get("category", "").strip()
        if category_slug:
            try:
                category = Category.objects.get(slug=category_slug, is_active=True)
            except Category.DoesNotExist as error:
                raise NotFound("产品分类不存在或未启用。") from error
            if category.parent_id:
                queryset = queryset.filter(category=category)
            else:
                queryset = queryset.filter(Q(category=category) | Q(category__parent=category))

        search = self.request.query_params.get("search", "").strip()
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(tag__icontains=search)
                | Q(summary__icontains=search)
                | Q(specification__icontains=search)
            )

        featured = self.request.query_params.get("featured", "").lower()
        if featured in {"1", "true", "yes"}:
            queryset = queryset.filter(is_featured=True)

        return queryset.order_by("sort_order", "id")


class AdminCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = AdminCategorySerializer
    queryset = Category.objects.select_related("parent").all()

class AdminProductViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = AdminProductSerializer
    queryset = Product.objects.select_related("category").prefetch_related("images")


class AdminProductImageViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = AdminProductImageSerializer
    queryset = ProductImage.objects.select_related("product").all()
