from django.contrib.auth import authenticate, login, logout
from django.http import Http404, HttpResponsePermanentRedirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView


class HealthView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"status": "ok", "service": "qiaonong-api"})


class LegacyRedirectView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        legacy_type = request.query_params.get("s", "")
        try:
            legacy_id = int(request.query_params.get("id", ""))
        except (TypeError, ValueError) as error:
            raise Http404 from error

        if legacy_type == "index/show/index":
            from apps.catalog.models import Product

            product = Product.objects.filter(legacy_id=legacy_id).only("slug").first()
            if product:
                return HttpResponsePermanentRedirect(f"/product/{product.slug}")
        elif legacy_type == "index/category/index":
            from apps.catalog.models import Category
            from apps.content.models import ContentPage

            category = Category.objects.filter(legacy_id=legacy_id).only("slug").first()
            if category:
                return HttpResponsePermanentRedirect(f"/products/{category.slug}")
            page_id = 1 if legacy_id == 46 else legacy_id
            page = ContentPage.objects.filter(legacy_id=page_id).only("slug").first()
            if page:
                if page.slug == "contact":
                    return HttpResponsePermanentRedirect("/contact")
                if page.slug == "brand":
                    return HttpResponsePermanentRedirect("/brand")
                return HttpResponsePermanentRedirect(f"/policy/{page.slug}")
        raise Http404


@method_decorator(ensure_csrf_cookie, name="dispatch")
class AdminSessionView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        user = request.user
        if not user.is_authenticated or not user.is_active or not user.is_staff:
            return Response({"authenticated": False, "user": None})
        return Response(
            {
                "authenticated": True,
                "user": {
                    "id": user.pk,
                    "username": user.get_username(),
                    "display_name": user.get_full_name() or user.get_username(),
                },
            }
        )


@method_decorator(csrf_protect, name="dispatch")
class AdminLoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "admin_login"

    def post(self, request):
        username = str(request.data.get("username", "")).strip()
        password = str(request.data.get("password", ""))
        user = authenticate(request, username=username, password=password)
        if user is None or not user.is_active or not user.is_staff:
            return Response(
                {"detail": "用户名或密码错误。"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        login(request, user)
        return Response(
            {
                "authenticated": True,
                "user": {
                    "id": user.pk,
                    "username": user.get_username(),
                    "display_name": user.get_full_name() or user.get_username(),
                },
            }
        )


@method_decorator(csrf_protect, name="dispatch")
class AdminLogoutView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)
