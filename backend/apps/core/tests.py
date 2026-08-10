import json

from django.contrib.auth import get_user_model
from django.test import Client, SimpleTestCase, TestCase
from django.urls import reverse


class HealthViewTests(SimpleTestCase):
    def test_health_check(self):
        response = self.client.get(reverse("health"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"status": "ok", "service": "qiaonong-api"},
        )


class AdminAuthTests(TestCase):
    def setUp(self):
        self.password = "strong-test-password"
        self.staff = get_user_model().objects.create_user(
            username="site-admin",
            password=self.password,
            is_staff=True,
        )
        self.client = Client(enforce_csrf_checks=True)

    def csrf_token(self):
        response = self.client.get(reverse("admin-session"))
        self.assertEqual(response.status_code, 200)
        return response.cookies["csrftoken"].value

    def test_session_endpoint_sets_csrf_cookie(self):
        response = self.client.get(reverse("admin-session"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"authenticated": False, "user": None})
        self.assertIn("csrftoken", response.cookies)

    def test_login_requires_csrf(self):
        response = self.client.post(
            reverse("admin-login"),
            data=json.dumps(
                {"username": self.staff.username, "password": self.password}
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 403)

    def test_staff_can_login_restore_session_and_logout(self):
        token = self.csrf_token()
        login_response = self.client.post(
            reverse("admin-login"),
            data=json.dumps(
                {"username": self.staff.username, "password": self.password}
            ),
            content_type="application/json",
            HTTP_X_CSRFTOKEN=token,
        )

        self.assertEqual(login_response.status_code, 200)
        self.assertTrue(login_response.json()["authenticated"])
        session_response = self.client.get(reverse("admin-session"))
        self.assertEqual(session_response.json()["user"]["username"], "site-admin")

        token = self.client.cookies["csrftoken"].value
        logout_response = self.client.post(
            reverse("admin-logout"), HTTP_X_CSRFTOKEN=token
        )
        self.assertEqual(logout_response.status_code, 204)
        self.assertFalse(self.client.get(reverse("admin-session")).json()["authenticated"])

    def test_non_staff_user_cannot_login(self):
        user = get_user_model().objects.create_user(
            username="public-user", password=self.password
        )
        token = self.csrf_token()

        response = self.client.post(
            reverse("admin-login"),
            data=json.dumps({"username": user.username, "password": self.password}),
            content_type="application/json",
            HTTP_X_CSRFTOKEN=token,
        )

        self.assertEqual(response.status_code, 400)
        self.assertNotIn("sessionid", response.cookies)


class LegacyRedirectTests(TestCase):
    def test_product_url_redirects_to_stable_public_url(self):
        from apps.catalog.models import Category, Product

        category = Category.objects.create(name="护肤", slug="skin-care")
        Product.objects.create(
            category=category,
            name="测试产品",
            slug="test-product",
            legacy_id=75,
        )

        response = self.client.get(
            reverse("legacy-redirect"),
            {"s": "index/show/index", "id": "75"},
        )

        self.assertEqual(response.status_code, 301)
        self.assertEqual(response["Location"], "/product/test-product")

    def test_unknown_legacy_url_returns_not_found(self):
        response = self.client.get(
            reverse("legacy-redirect"), {"s": "index/show/index", "id": "9999"}
        )

        self.assertEqual(response.status_code, 404)


class SeoViewTests(TestCase):
    def setUp(self):
        from apps.catalog.models import Category, Product
        from apps.content.models import ContentPage, SiteSettings

        self.category = Category.objects.create(
            name="护肤系列",
            slug="skin-care",
            description="巧侬护肤系列介绍",
            is_active=True,
        )
        self.product = Product.objects.create(
            category=self.category,
            name="保湿精华",
            slug="moisture-serum",
            summary="温和保湿产品资料",
            description="产品详情正文",
            is_active=True,
        )
        SiteSettings.objects.create(
            site_name="巧侬花田",
            home_title="巧侬花田",
            home_subtitle="巧侬品牌与产品资料",
        )
        ContentPage.objects.create(
            slug="brand",
            title="品牌介绍",
            summary="巧侬品牌介绍摘要",
            body="巧侬品牌介绍正文",
            is_active=True,
        )

    def test_home_contains_crawlable_content_and_canonical(self):
        response = self.client.get(reverse("seo-home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "巧侬花田官网 - 护肤、院护与医美产品")
        self.assertContains(response, "https://zgqnht.com/")
        self.assertContains(response, "护肤系列")
        self.assertContains(response, 'application/ld+json')

    def test_product_detail_contains_product_content(self):
        response = self.client.get(
            reverse("seo-product-detail", kwargs={"slug": self.product.slug})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "保湿精华 - 巧侬花田")
        self.assertContains(response, "温和保湿产品资料")
        self.assertContains(response, '"@type": "Product"')

    def test_unknown_product_and_category_return_not_found(self):
        self.assertEqual(
            self.client.get(
                reverse("seo-product-detail", kwargs={"slug": "missing"})
            ).status_code,
            404,
        )
        self.assertEqual(
            self.client.get(
                reverse("seo-product-list", kwargs={"slug": "missing"})
            ).status_code,
            404,
        )

    def test_robots_and_sitemap_are_real_crawler_resources(self):
        robots = self.client.get(reverse("robots"))
        sitemap = self.client.get(reverse("sitemap"))

        self.assertEqual(robots["Content-Type"], "text/plain; charset=utf-8")
        self.assertContains(robots, "Sitemap: https://zgqnht.com/sitemap.xml")
        self.assertEqual(sitemap["Content-Type"], "application/xml; charset=utf-8")
        self.assertContains(sitemap, "https://zgqnht.com/product/moisture-serum")
        self.assertContains(sitemap, "https://zgqnht.com/products/skin-care")
