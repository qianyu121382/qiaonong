from django.urls import path

from .views import AdminLoginView, AdminLogoutView, AdminSessionView, HealthView


urlpatterns = [
    path("health/", HealthView.as_view(), name="health"),
    path("admin/auth/me/", AdminSessionView.as_view(), name="admin-session"),
    path("admin/auth/login/", AdminLoginView.as_view(), name="admin-login"),
    path("admin/auth/logout/", AdminLogoutView.as_view(), name="admin-logout"),
]
