from rest_framework import generics, viewsets
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ContentPage, HeroSlide, SiteSettings
from .serializers import (
    AdminSiteSettingsSerializer,
    ContentPageSerializer,
    HeroSlideSerializer,
    SiteSettingsSerializer,
)


class PublicSiteSettingsView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        settings = SiteSettings.objects.first() or SiteSettings()
        return Response(SiteSettingsSerializer(settings, context={"request": request}).data)


class PublicHeroSlideViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = HeroSlideSerializer
    queryset = HeroSlide.objects.filter(is_active=True)


class PublicContentPageViewSet(viewsets.ReadOnlyModelViewSet):
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = ContentPageSerializer
    lookup_field = "slug"
    queryset = ContentPage.objects.filter(is_active=True)


class AdminSiteSettingsView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = AdminSiteSettingsSerializer

    def get_object(self):
        settings, _ = SiteSettings.objects.get_or_create(pk=1)
        return settings


class AdminHeroSlideViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = HeroSlideSerializer
    queryset = HeroSlide.objects.all()


class AdminContentPageViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = ContentPageSerializer
    queryset = ContentPage.objects.all()
