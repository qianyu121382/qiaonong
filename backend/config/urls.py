from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from apps.core.views import LegacyRedirectView


urlpatterns = [
    path("index.php", LegacyRedirectView.as_view(), name="legacy-redirect"),
    path("admin/", admin.site.urls),
    path("api/", include("apps.core.urls")),
    path("api/catalog/", include("apps.catalog.urls")),
    path("api/admin/catalog/", include("apps.catalog.admin_urls")),
    path("api/content/", include("apps.content.urls")),
    path("api/admin/content/", include("apps.content.admin_urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
