from rest_framework.routers import SimpleRouter

from .views import PublicCategoryViewSet, PublicProductViewSet


router = SimpleRouter()
router.register("categories", PublicCategoryViewSet, basename="public-category")
router.register("products", PublicProductViewSet, basename="public-product")

urlpatterns = router.urls
