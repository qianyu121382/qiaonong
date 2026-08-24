from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from .models import Category, Product


class CatalogModelTests(TestCase):
    def test_category_depth_is_limited_to_two_levels(self):
        root = Category.objects.create(name="护肤", slug="skin-care")
        child = Category.objects.create(
            name="保湿系列", slug="hydrating", parent=root
        )
        grandchild = Category(name="不允许的第三级", slug="level-three", parent=child)

        with self.assertRaises(DjangoValidationError):
            grandchild.full_clean()

    def test_category_with_children_cannot_become_a_child(self):
        root = Category.objects.create(name="护肤", slug="skin-care")
        Category.objects.create(name="面膜", slug="masks", parent=root)
        another_root = Category.objects.create(name="院护", slug="salon-care")
        root.parent = another_root

        with self.assertRaises(DjangoValidationError):
            root.full_clean()


class PublicCatalogApiTests(TestCase):
    def setUp(self):
        self.root = Category.objects.create(
            name="护肤", slug="skin-care", sort_order=1
        )
        self.child = Category.objects.create(
            name="保湿系列", slug="hydrating", parent=self.root, sort_order=1
        )
        self.inactive_root = Category.objects.create(
            name="停用系列", slug="inactive-series", is_active=False
        )
        self.hidden_child = Category.objects.create(
            name="被上级隐藏", slug="hidden-child", parent=self.inactive_root
        )
        self.direct_product = Product.objects.create(
            category=self.root,
            name="直接归属一级的产品",
            slug="root-product",
            summary="舒缓修护",
            is_active=True,
            sort_order=2,
        )
        self.child_product = Product.objects.create(
            category=self.child,
            name="透明质酸保湿精华",
            slug="hydrating-serum",
            tag="补水",
            summary="日常保湿",
            is_active=True,
            is_featured=True,
            sort_order=1,
        )
        Product.objects.create(
            category=self.child,
            name="下架产品",
            slug="inactive-product",
            is_active=False,
        )
        Product.objects.create(
            category=self.hidden_child,
            name="上级停用后隐藏的产品",
            slug="hidden-by-parent",
            is_active=True,
        )

    def test_category_list_returns_active_roots_with_active_children(self):
        response = self.client.get(reverse("public-category-list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual([item["slug"] for item in response.json()], ["skin-care"])
        self.assertEqual(response.json()[0]["children"][0]["slug"], "hydrating")

    def test_products_hide_inactive_content(self):
        response = self.client.get(reverse("public-product-list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [item["slug"] for item in response.json()],
            ["hydrating-serum", "root-product"],
        )

    def test_root_category_filter_includes_direct_and_child_products(self):
        response = self.client.get(
            reverse("public-product-list"), {"category": self.root.slug}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            {item["slug"] for item in response.json()},
            {"root-product", "hydrating-serum"},
        )

    def test_search_and_featured_filters(self):
        search_response = self.client.get(
            reverse("public-product-list"), {"search": "透明质酸"}
        )
        featured_response = self.client.get(
            reverse("public-product-list"), {"featured": "true"}
        )

        self.assertEqual(
            [item["slug"] for item in search_response.json()], ["hydrating-serum"]
        )
        self.assertEqual(
            [item["slug"] for item in featured_response.json()],
            ["hydrating-serum"],
        )

    def test_hidden_product_detail_returns_not_found(self):
        response = self.client.get(
            reverse("public-product-detail", kwargs={"slug": "hidden-by-parent"})
        )

        self.assertEqual(response.status_code, 404)


class AdminCatalogApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.staff = get_user_model().objects.create_user(
            username="catalog-admin",
            password="test-password",
            is_staff=True,
        )

    def test_anonymous_user_cannot_access_management_api(self):
        response = self.client.get(reverse("admin-category-list"))

        self.assertEqual(response.status_code, 403)

    def test_staff_user_can_create_and_update_categories(self):
        self.client.force_authenticate(self.staff)

        root = Category.objects.create(name="护肤", slug="skin-care")
        list_response = self.client.get(reverse("admin-category-list"))
        create_response = self.client.post(
            reverse("admin-category-list"),
            {
                "name": "面膜系列",
                "slug": "customer-supplied-slug",
                "legacy_id": 999,
                "parent": root.pk,
                "sort_order": 3,
            },
            format="json",
        )

        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(create_response.status_code, 201)
        category = Category.objects.get(pk=create_response.json()["id"])
        self.assertTrue(category.slug.startswith("category-"))
        self.assertNotEqual(category.slug, "customer-supplied-slug")
        self.assertIsNone(category.legacy_id)
        self.assertEqual(category.parent, root)

        update_response = self.client.patch(
            reverse("admin-category-detail", kwargs={"pk": category.pk}),
            {"name": "修护面膜系列", "is_active": False},
            format="json",
        )
        self.assertEqual(update_response.status_code, 200)
        category.refresh_from_db()
        self.assertEqual(category.name, "修护面膜系列")
        self.assertFalse(category.is_active)

        promote_response = self.client.patch(
            reverse("admin-category-detail", kwargs={"pk": category.pk}),
            {"parent": ""},
            format="multipart",
        )
        self.assertEqual(promote_response.status_code, 200)
        category.refresh_from_db()
        self.assertIsNone(category.parent)

    def test_staff_user_can_delete_unreferenced_category(self):
        category = Category.objects.create(name="待删除分类", slug="unused")
        self.client.force_authenticate(self.staff)

        delete_response = self.client.delete(
            reverse("admin-category-detail", kwargs={"pk": category.pk})
        )

        self.assertEqual(delete_response.status_code, 204)
        self.assertFalse(Category.objects.filter(pk=category.pk).exists())

    def test_staff_user_cannot_delete_category_with_children_or_products(self):
        root = Category.objects.create(name="护肤", slug="skin-care")
        child = Category.objects.create(name="面膜", slug="masks", parent=root)
        Product.objects.create(category=child, name="面膜", slug="mask-product")
        self.client.force_authenticate(self.staff)

        root_response = self.client.delete(
            reverse("admin-category-detail", kwargs={"pk": root.pk})
        )
        child_response = self.client.delete(
            reverse("admin-category-detail", kwargs={"pk": child.pk})
        )

        self.assertEqual(root_response.status_code, 400)
        self.assertIn("下级分类", root_response.json()["detail"])
        self.assertEqual(child_response.status_code, 400)
        self.assertIn("关联产品", child_response.json()["detail"])

    def test_staff_user_cannot_create_a_third_category_level(self):
        root = Category.objects.create(name="护肤", slug="skin-care")
        child = Category.objects.create(name="面膜", slug="masks", parent=root)
        self.client.force_authenticate(self.staff)

        response = self.client.post(
            reverse("admin-category-list"),
            {"name": "第三级", "parent": child.pk},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(Category.objects.filter(name="第三级").exists())

    def test_product_slug_and_legacy_id_are_server_managed(self):
        category = Category.objects.create(name="护肤", slug="skin-care")
        self.client.force_authenticate(self.staff)

        response = self.client.post(
            reverse("admin-product-list"),
            {
                "category": category.pk,
                "name": "新产品",
                "slug": "customer-supplied-slug",
                "legacy_id": 999,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        product = Product.objects.get(pk=response.json()["id"])
        self.assertTrue(product.slug.startswith("product-"))
        self.assertNotEqual(product.slug, "customer-supplied-slug")
        self.assertIsNone(product.legacy_id)
