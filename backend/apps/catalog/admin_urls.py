from rest_framework.routers import SimpleRouter

from .views import (
    AdminCategoryViewSet,
    AdminProductImageViewSet,
    AdminProductViewSet,
)


router = SimpleRouter()
router.register("categories", AdminCategoryViewSet, basename="admin-category")
router.register("products", AdminProductViewSet, basename="admin-product")
router.register("product-images", AdminProductImageViewSet, basename="admin-product-image")

urlpatterns = router.urls
