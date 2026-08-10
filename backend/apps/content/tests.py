from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from .models import ContentPage, SiteSettings


class PublicContentApiTests(TestCase):
    def test_site_settings_has_safe_defaults_before_configuration(self):
        response = self.client.get(reverse("public-site-settings"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["site_name"], "巧侬")
        self.assertEqual(response.json()["company_name"], "")

    def test_only_active_content_pages_are_public(self):
        ContentPage.objects.create(slug="brand", title="品牌介绍", is_active=True)
        ContentPage.objects.create(slug="privacy", title="隐私条款", is_active=False)

        list_response = self.client.get(reverse("public-content-page-list"))
        hidden_response = self.client.get(
            reverse("public-content-page-detail", kwargs={"slug": "privacy"})
        )

        self.assertEqual(
            [page["slug"] for page in list_response.json()], ["brand"]
        )
        self.assertEqual(hidden_response.status_code, 404)


class AdminContentApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.staff = get_user_model().objects.create_user(
            username="content-admin", password="test-password", is_staff=True
        )

    def test_anonymous_user_cannot_read_management_content(self):
        response = self.client.get(reverse("admin-site-settings"))

        self.assertEqual(response.status_code, 403)

    def test_staff_can_update_single_site_settings_record(self):
        self.client.force_authenticate(self.staff)

        response = self.client.patch(
            reverse("admin-site-settings"),
            {"site_name": "巧侬官网", "phone": "待确认"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(SiteSettings.objects.count(), 1)
        self.assertEqual(SiteSettings.objects.get().site_name, "巧侬官网")

    def test_staff_can_create_and_publish_content_page(self):
        self.client.force_authenticate(self.staff)

        response = self.client.post(
            reverse("admin-content-page-list"),
            {
                "slug": "brand",
                "title": "品牌介绍",
                "body": "经确认的品牌内容",
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        public_response = self.client.get(
            reverse("public-content-page-detail", kwargs={"slug": "brand"})
        )
        self.assertEqual(public_response.status_code, 200)
