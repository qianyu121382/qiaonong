from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from apps.core.views import LegacyRedirectView
from apps.core.seo_views import (
    ContentSeoView,
    HomeSeoView,
    ProductDetailSeoView,
    ProductListSeoView,
    RobotsView,
    SearchSeoView,
    SitemapView,
)


urlpatterns = [
    path("robots.txt", RobotsView.as_view(), name="robots"),
    path("sitemap.xml", SitemapView.as_view(), name="sitemap"),
    path("index.php", LegacyRedirectView.as_view(), name="legacy-redirect"),
    path("admin/", admin.site.urls),
    path("api/", include("apps.core.urls")),
    path("api/catalog/", include("apps.catalog.urls")),
    path("api/admin/catalog/", include("apps.catalog.admin_urls")),
    path("api/content/", include("apps.content.urls")),
    path("api/admin/content/", include("apps.content.admin_urls")),
    path("", HomeSeoView.as_view(), name="seo-home"),
    path("brand", ContentSeoView.as_view(), {"slug": "brand"}, name="seo-brand"),
    path("contact", ContentSeoView.as_view(), {"slug": "contact"}, name="seo-contact"),
    path("products", ProductListSeoView.as_view(), name="seo-products"),
    path("products/<slug:slug>", ProductListSeoView.as_view(), name="seo-product-list"),
    path("product/<slug:slug>", ProductDetailSeoView.as_view(), name="seo-product-detail"),
    path("policy/<slug:slug>", ContentSeoView.as_view(), name="seo-content"),
    path("search", SearchSeoView.as_view(), name="seo-search"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
