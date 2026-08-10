from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import PublicContentPageViewSet, PublicHeroSlideViewSet, PublicSiteSettingsView


router = SimpleRouter()
router.register("slides", PublicHeroSlideViewSet, basename="public-slide")
router.register("pages", PublicContentPageViewSet, basename="public-content-page")

urlpatterns = [path("site/", PublicSiteSettingsView.as_view(), name="public-site-settings")]
urlpatterns += router.urls
