from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from kitchen.models import DishType


class DishTypeListViewTests(TestCase):
    def setUp(self):
        self.url = reverse("kitchen:dish-type-list")

    def test_template_and_context(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "kitchen/dish_type_list.html")
        self.assertIn("dish_type_list", response.context)
        self.assertIn("search_form", response.context)

    def test_queryset_no_filter_returns_all(self):
        DishType.objects.create(name="Soup")
        DishType.objects.create(name="Salad")

        response = self.client.get(self.url)
        dish_types = DishType.objects.all()
        self.assertEqual(
            list(response.context["dish_type_list"]),
            list(dish_types)
        )

    def test_queryset_with_filter_returns_matching(self):
        DishType.objects.create(name="Soup")
        DishType.objects.create(name="Salad")

        response = self.client.get(self.url, {"name": "sou"})
        dish_types = DishType.objects.filter(name__icontains="sou")
        self.assertEqual(
            list(response.context["dish_type_list"]),
            list(dish_types)
        )

    def test_queryset_with_filter_no_match(self):
        DishType.objects.create(name="Soup")

        response = self.client.get(self.url, {"name": "pizza"})
        self.assertEqual(list(response.context["dish_type_list"]), [])

    def test_pagination_first_page(self):
        DishType.objects.bulk_create(
            [DishType(name=f"Dish {i}") for i in range(15)]
        )

        response = self.client.get(self.url)
        page_obj = response.context["page_obj"]

        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(page_obj.paginator.num_pages, 2)
        self.assertEqual(len(response.context["dish_type_list"]), 10)

    def test_pagination_second_page(self):
        DishType.objects.bulk_create(
            [DishType(name=f"Dish {i}") for i in range(15)]
        )

        response = self.client.get(self.url, {"page": 2})
        page_obj = response.context["page_obj"]

        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(page_obj.paginator.num_pages, 2)
        self.assertEqual(len(response.context["dish_type_list"]), 5)

    def test_empty_database(self):
        response = self.client.get(self.url)
        self.assertEqual(list(response.context["dish_type_list"]), [])


class PublicDishTypeCreateViewTests(TestCase):
    def setUp(self):
        self.url = reverse("kitchen:dish-type-create")
        self.user = get_user_model().objects.create_user(
            username="test-user",
            password="password1234"
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        login_url = reverse("login")
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f"{login_url}?next={self.url}")


class PrivateDishTypeCreateViewTests(TestCase):
    def setUp(self):
        self.url = reverse("kitchen:dish-type-create")
        self.user = get_user_model().objects.create_user(
            username="test-user",
            password="password1234"
        )
        self.client.force_login(self.user)

    def test_logged_in_user_can_access_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "kitchen/dish_type_form.html")
        self.assertIn("form", response.context)

    def test_create_dish_type_valid_post(self):
        data = {"name": "Salad"}
        response = self.client.post(self.url, data)
        self.assertEqual(DishType.objects.count(), 1)
        self.assertEqual(DishType.objects.first().name, "Salad")
        self.assertRedirects(response, reverse("kitchen:dish-type-list"))

    def test_create_dish_type_invalid_post(self):
        response = self.client.post(self.url, {"name": ""})
        form = response.context["form"]
        self.assertTrue(form.errors)
        self.assertIn("name", form.errors)
        self.assertEqual(form.errors["name"], ["This field is required."])
        self.assertEqual(DishType.objects.count(), 0)


class PublicDishTypeUpdateViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="test-user",
            password="password123"
        )
        self.dish_type = DishType.objects.create(name="Soup")
        self.url = reverse(
            "kitchen:dish-type-update",
            args=[self.dish_type.id]
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")


class PrivateDishTypeUpdateViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="test-user",
            password="password123"
        )
        self.client.force_login(self.user)
        self.dish_type = DishType.objects.create(name="Soup")
        self.url = reverse(
            "kitchen:dish-type-update",
            args=[self.dish_type.id]
        )

    def test_logged_in_user_can_access_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "kitchen/dish_type_form.html")
        self.assertIn("form", response.context)
        self.assertEqual(response.context["form"].initial["name"], "Soup")

    def test_update_dish_type_valid_post(self):
        response = self.client.post(self.url, {"name": "Salad"})
        self.dish_type.refresh_from_db()
        self.assertEqual(self.dish_type.name, "Salad")
        self.assertRedirects(response, reverse("kitchen:dish-type-list"))

    def test_update_dish_type_invalid_post(self):
        response = self.client.post(self.url, {"name": ""})
        form = response.context["form"]
        self.assertTrue(form.errors)
        self.dish_type.refresh_from_db()
        self.assertEqual(self.dish_type.name, "Soup")

    def test_update_nonexistent_object_returns_404(self):
        bad_url = reverse("kitchen:dish-type-update", args=[999])
        response = self.client.get(bad_url)
        self.assertEqual(response.status_code, 404)


class PublicDishTypeDeleteViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="test-user",
            password="password1234"
        )
        self.dish_type = DishType.objects.create(name="Soup")
        self.url = reverse(
            "kitchen:dish-type-delete",
            args=[self.dish_type.id]
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")


class PrivateDishTypeDeleteViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="test-user",
            password="password1234"
        )
        self.client.force_login(self.user)
        self.dish_type = DishType.objects.create(name="Soup")
        self.url = reverse(
            "kitchen:dish-type-delete",
            args=[self.dish_type.id]
        )

    def test_logged_in_user_can_access_confirmation_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "kitchen/confirm_delete_dish_type.html"
        )
        self.assertEqual(response.context["object"], self.dish_type)

    def test_delete_dish_type_valid_post(self):
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse("kitchen:dish-type-list"))
        self.assertFalse(
            DishType.objects.filter(id=self.dish_type.id).exists()
        )

    def test_get_request_does_not_delete_object(self):
        self.client.get(self.url)
        self.assertTrue(DishType.objects.filter(id=self.dish_type.id).exists())

    def test_delete_nonexistent_object_returns_404(self):
        bad_url = reverse("kitchen:dish-type-delete", args=[999])
        response = self.client.get(bad_url)
        self.assertEqual(response.status_code, 404)
