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
