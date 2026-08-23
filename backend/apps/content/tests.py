from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from .models import ContentPage, HeroSlide, SiteSettings


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

    def test_slide_api_exposes_desktop_and_optional_mobile_images(self):
        HeroSlide.objects.create(
            image="content/slides/desktop.webp",
            mobile_image="content/slides/mobile.webp",
            is_active=True,
        )

        response = self.client.get(reverse("public-slide-list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertTrue(
            response.json()[0]["image"].endswith(
                "/media/content/slides/desktop.webp"
            )
        )
        self.assertTrue(
            response.json()[0]["mobile_image"].endswith(
                "/media/content/slides/mobile.webp"
            )
        )


class AdminContentApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.staff = get_user_model().objects.create_user(
            username="content-admin", password="test-password", is_staff=True
        )

    def test_anonymous_user_cannot_read_management_content(self):
        response = self.client.get(reverse("admin-site-settings"))

        self.assertEqual(response.status_code, 403)

    def test_staff_can_update_only_company_information(self):
        settings = SiteSettings.objects.create(
            site_name="巧侬",
            home_title="固定首页标题",
        )
        self.client.force_authenticate(self.staff)

        response = self.client.patch(
            reverse("admin-site-settings"),
            {
                "site_name": "不允许修改的网站名称",
                "home_title": "不允许修改的首页标题",
                "company_name": "鞍山鼎禾生物制药有限公司",
                "phone": "待确认",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(SiteSettings.objects.count(), 1)
        settings.refresh_from_db()
        self.assertEqual(settings.site_name, "巧侬")
        self.assertEqual(settings.home_title, "固定首页标题")
        self.assertEqual(settings.company_name, "鞍山鼎禾生物制药有限公司")
        self.assertEqual(settings.phone, "待确认")

    def test_staff_can_read_content_pages_but_cannot_modify_them(self):
        page = ContentPage.objects.create(
            slug="brand", title="品牌介绍", is_active=True
        )
        self.client.force_authenticate(self.staff)

        list_response = self.client.get(reverse("admin-content-page-list"))
        create_response = self.client.post(
            reverse("admin-content-page-list"),
            {
                "slug": "privacy",
                "title": "隐私条款",
                "body": "经确认的品牌内容",
                "is_active": True,
            },
            format="json",
        )
        update_response = self.client.patch(
            reverse("admin-content-page-detail", kwargs={"pk": page.pk}),
            {"title": "被修改"},
            format="json",
        )
        delete_response = self.client.delete(
            reverse("admin-content-page-detail", kwargs={"pk": page.pk})
        )

        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(create_response.status_code, 405)
        self.assertEqual(update_response.status_code, 405)
        self.assertEqual(delete_response.status_code, 405)
        page.refresh_from_db()
        self.assertEqual(page.title, "品牌介绍")
