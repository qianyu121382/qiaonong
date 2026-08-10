from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import AdminContentPageViewSet, AdminHeroSlideViewSet, AdminSiteSettingsView


router = SimpleRouter()
router.register("slides", AdminHeroSlideViewSet, basename="admin-slide")
router.register("pages", AdminContentPageViewSet, basename="admin-content-page")

urlpatterns = [path("site/", AdminSiteSettingsView.as_view(), name="admin-site-settings")]
urlpatterns += router.urls
