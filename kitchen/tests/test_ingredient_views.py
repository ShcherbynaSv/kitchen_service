from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from kitchen.models import Ingredient


class IngredientListViewTests(TestCase):
    def setUp(self):
        self.url = reverse("kitchen:ingredient-list")

    def test_template_and_context(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "kitchen/ingredient_list.html")
        self.assertIn("ingredient_list", response.context)
        self.assertIn("search_form", response.context)

    def test_queryset_no_filter_returns_all(self):
        Ingredient.objects.create(name="Salt")
        Ingredient.objects.create(name="Pepper")

        response = self.client.get(self.url)
        ingredients = Ingredient.objects.all()
        self.assertEqual(
            list(response.context["ingredient_list"]),
            list(ingredients)
        )

    def test_queryset_with_filter_returns_matching(self):
        Ingredient.objects.create(name="Salt")
        Ingredient.objects.create(name="Pepper")

        response = self.client.get(self.url, {"name": "pep"})
        ingredients = Ingredient.objects.filter(name__icontains="pep")
        self.assertEqual(
            list(response.context["ingredient_list"]),
            list(ingredients)
        )

    def test_queryset_with_filter_no_match(self):
        Ingredient.objects.create(name="Salt")

        response = self.client.get(self.url, {"name": "pepper"})
        self.assertEqual(list(response.context["ingredient_list"]), [])

    def test_pagination_first_page(self):
        Ingredient.objects.bulk_create(
            [Ingredient(name=f"Ingredient {i}") for i in range(15)]
        )

        response = self.client.get(self.url)
        page_obj = response.context["page_obj"]

        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(page_obj.paginator.num_pages, 2)
        self.assertEqual(len(response.context["ingredient_list"]), 10)

    def test_pagination_second_page(self):
        Ingredient.objects.bulk_create(
            [Ingredient(name=f"Ingredient {i}") for i in range(15)]
        )

        response = self.client.get(self.url, {"page": 2})
        page_obj = response.context["page_obj"]

        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(page_obj.paginator.num_pages, 2)
        self.assertEqual(len(response.context["ingredient_list"]), 5)

    def test_empty_database(self):
        response = self.client.get(self.url)
        self.assertEqual(list(response.context["ingredient_list"]), [])


class PublicIngredientCreateViewTests(TestCase):
    def setUp(self):
        self.url = reverse("kitchen:ingredient-create")
        self.user = get_user_model().objects.create_user(
            username="test-user",
            password="password1234"
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        login_url = reverse("login")
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f"{login_url}?next={self.url}")


class PrivateIngredientCreateViewTests(TestCase):
    def setUp(self):
        self.url = reverse("kitchen:ingredient-create")
        self.user = get_user_model().objects.create_user(
            username="test-user",
            password="password1234"
        )
        self.client.force_login(self.user)

    def test_logged_in_user_can_access_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "kitchen/ingredient_form.html")
        self.assertIn("form", response.context)

    def test_create_ingredient_valid_post(self):
        data = {"name": "Salt"}
        response = self.client.post(self.url, data)
        self.assertEqual(Ingredient.objects.count(), 1)
        self.assertEqual(Ingredient.objects.first().name, "Salt")
        self.assertRedirects(response, reverse("kitchen:ingredient-list"))

    def test_create_ingredient_invalid_post(self):
        response = self.client.post(self.url, {"name": ""})
        form = response.context["form"]
        self.assertTrue(form.errors)
        self.assertIn("name", form.errors)
        self.assertEqual(form.errors["name"], ["This field is required."])
        self.assertEqual(Ingredient.objects.count(), 0)


class PublicIngredientUpdateViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="test-user",
            password="password123"
        )
        self.ingredient = Ingredient.objects.create(name="Salt")
        self.url = reverse(
            "kitchen:ingredient-update",
            args=[self.ingredient.id]
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")


class PrivateIngredientUpdateViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="test-user",
            password="password123"
        )
        self.client.force_login(self.user)
        self.ingredient = Ingredient.objects.create(name="Salt")
        self.url = reverse(
            "kitchen:ingredient-update",
            args=[self.ingredient.id]
        )

    def test_logged_in_user_can_access_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "kitchen/ingredient_form.html")
        self.assertIn("form", response.context)
        self.assertEqual(response.context["form"].initial["name"], "Salt")

    def test_update_ingredient_valid_post(self):
        response = self.client.post(self.url, {"name": "Pepper"})
        self.ingredient.refresh_from_db()
        self.assertEqual(self.ingredient.name, "Pepper")
        self.assertRedirects(response, reverse("kitchen:ingredient-list"))

    def test_update_ingredient_invalid_post(self):
        response = self.client.post(self.url, {"name": ""})
        form = response.context["form"]
        self.assertTrue(form.errors)
        self.ingredient.refresh_from_db()
        self.assertEqual(self.ingredient.name, "Salt")

    def test_update_nonexistent_object_returns_404(self):
        bad_url = reverse("kitchen:ingredient-update", args=[999])
        response = self.client.get(bad_url)
        self.assertEqual(response.status_code, 404)


class PublicIngredientDeleteViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="test-user",
            password="password1234"
        )
        self.ingredient = Ingredient.objects.create(name="Soup")
        self.url = reverse(
            "kitchen:ingredient-delete",
            args=[self.ingredient.id]
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f"{reverse('login')}?next={self.url}")


class PrivateIngredientDeleteViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="test-user",
            password="password1234"
        )
        self.client.force_login(self.user)
        self.ingredient = Ingredient.objects.create(name="Salt")
        self.url = reverse(
            "kitchen:ingredient-delete",
            args=[self.ingredient.id]
        )

    def test_logged_in_user_can_access_confirmation_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "kitchen/confirm_delete_ingredient.html"
        )
        self.assertEqual(response.context["object"], self.ingredient)

    def test_delete_ingredient_valid_post(self):
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse("kitchen:ingredient-list"))
        self.assertFalse(
            Ingredient.objects.filter(id=self.ingredient.id).exists()
        )

    def test_get_request_does_not_delete_object(self):
        self.client.get(self.url)
        self.assertTrue(
            Ingredient.objects.filter(id=self.ingredient.id).exists()
        )

    def test_delete_nonexistent_object_returns_404(self):
        bad_url = reverse("kitchen:ingredient-delete", args=[999])
        response = self.client.get(bad_url)
        self.assertEqual(response.status_code, 404)
