from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from kitchen.models import Dish, DishType, Ingredient
from kitchen.forms import DishSearchForm


class DishListViewTests(TestCase):
    def setUp(self):
        self.url = reverse("kitchen:dish-list")
        self.dish_type_1 = DishType.objects.create(name="Salad")
        self.dish_type_2 = DishType.objects.create(name="Soup")
        self.ingredient_1 = Ingredient.objects.create(name="Salt")
        self.ingredient_2 = Ingredient.objects.create(name="Pepper")
        self.dish_1 = Dish.objects.create(
            name="Caesar",
            price=10.5,
            description="test-description",
            dish_type=self.dish_type_1
        )
        self.dish_1.ingredients.add(self.ingredient_1)
        self.dish_2 = Dish.objects.create(
            name="Minestrone",
            price=20.5,
            description="test-description",
            dish_type=self.dish_type_2
        )
        self.dish_2.ingredients.add(self.ingredient_2)

    def test_template_and_context(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "kitchen/dish_list.html")
        self.assertIn("dishes_list", response.context)
        self.assertIn("search_form", response.context)
        self.assertIn("selected_dish_type", response.context)
        self.assertIn("selected_ingredient", response.context)

    def test_queryset_no_filter_returns_all(self):
        response = self.client.get(self.url)
        self.assertEqual(
            list(response.context["dishes_list"]), [self.dish_1, self.dish_2])

    def test_filter_by_ingredient(self):
        response = self.client.get(
            self.url,
            {"ingredients": self.ingredient_1.id}
        )
        self.assertIn(self.dish_1, response.context["dishes_list"])
        self.assertNotIn(self.dish_2, response.context["dishes_list"])
        self.assertEqual(
            response.context["selected_ingredient"],
            self.ingredient_1
        )

    def test_filter_by_dish_type(self):
        response = self.client.get(
            self.url,
            {"dish_type": self.dish_type_1.id}
        )
        self.assertIn(self.dish_1, response.context["dishes_list"])
        self.assertNotIn(self.dish_2, response.context["dishes_list"])
        self.assertEqual(
            response.context["selected_dish_type"],
            self.dish_type_1
        )

    def test_filter_by_name(self):
        response = self.client.get(self.url, {"name": "cae"})
        self.assertIn(self.dish_1, response.context["dishes_list"])
        self.assertNotIn(self.dish_2, response.context["dishes_list"])
        self.assertIsInstance(response.context["search_form"], DishSearchForm)
        self.assertEqual(
            response.context["search_form"].initial.get("name"), "cae"
        )

    def test_combined_filters(self):
        response = self.client.get(
            self.url,
            {
                "dish_type": self.dish_type_1.id,
                "ingredients": self.ingredient_1.id,
                "name": "cae"
            }
        )
        self.assertIn(self.dish_1, response.context["dishes_list"])
        self.assertNotIn(self.dish_2, response.context["dishes_list"])

    def test_pagination(self):
        [
            Dish.objects.create(
                name=f"Dish {i}",
                price=10 + i,
                description=f"test-description {i}",
                dish_type=self.dish_type_1
            )
            for i in range(15)
        ]
        response = self.client.get(self.url)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["dishes_list"]), 10)

        response = self.client.get(self.url, {"page": 2})
        self.assertEqual(len(response.context["dishes_list"]), 7)

    def test_empty_database(self):
        response = self.client.get(self.url)
        self.assertEqual(
            list(response.context["dishes_list"]),
            [self.dish_1, self.dish_2]
        )


class DishDetailViewTests(TestCase):
    def setUp(self):
        self.dish_type = DishType.objects.create(name="Salad")
        self.ingredient = Ingredient.objects.create(name="Salt")
        self.cook = get_user_model().objects.create_user(
            username="chef",
            password="pass"
        )
        self.dish = Dish.objects.create(
            name="Caesar",
            price=10.5,
            description="test-description",
            dish_type=self.dish_type)
        self.dish.ingredients.add(self.ingredient)
        self.dish.cooks.add(self.cook)
        self.url = reverse("kitchen:dish-detail", args=[self.dish.id])

    def test_detail_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "kitchen/dish_detail.html")
        self.assertEqual(response.context["dish"], self.dish)

    def test_context_includes_related_objects(self):
        response = self.client.get(self.url)
        dish = response.context["dish"]
        self.assertEqual(dish.dish_type, self.dish_type)
        self.assertIn(self.ingredient, dish.ingredients.all())
        self.assertIn(self.cook, dish.cooks.all())

    def test_nonexistent_dish_returns_404(self):
        bad_url = reverse("kitchen:dish-detail", args=[999])
        response = self.client.get(bad_url)
        self.assertEqual(response.status_code, 404)


class PublicDishCreateViewTests(TestCase):
    def setUp(self):
        self.url = reverse("kitchen:dish-create")

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        login_url = reverse("login")
        self.assertRedirects(response, f"{login_url}?next={self.url}")


class PrivateDishCreateViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="user", password="password123"
        )
        self.client.force_login(self.user)
        self.dish_type = DishType.objects.create(name="Salad")
        self.ingredient = Ingredient.objects.create(name="Salt")
        self.url = reverse("kitchen:dish-create")

    def test_access_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "kitchen/dish_form.html")
        self.assertIn("form", response.context)

    def test_create_valid_dish(self):
        data = {
            "name": "Caesar",
            "price": 10.5,
            "description": "test-description",
            "dish_type": self.dish_type.id,
            "ingredients": [self.ingredient.id]
        }
        response = self.client.post(self.url, data)
        dish = Dish.objects.get(name="Caesar")
        self.assertEqual(dish.price, 10.5)
        self.assertEqual(dish.description, "test-description")
        self.assertEqual(dish.dish_type, self.dish_type)
        self.assertIn(self.ingredient, dish.ingredients.all())
        self.assertRedirects(response, reverse("kitchen:dish-list"))

    def test_create_invalid_dish(self):
        response = self.client.post(self.url, {"name": ""})
        self.assertTrue(response.context["form"].errors)
        self.assertEqual(Dish.objects.count(), 0)


class PublicDishUpdateViewTests(TestCase):
    def setUp(self):
        self.dish_type = DishType.objects.create(name="Salad")
        self.dish = Dish.objects.create(
            name="Caesar",
            price=10.5,
            description="desc",
            dish_type=self.dish_type
        )
        self.url = reverse("kitchen:dish-update", args=[self.dish.id])

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        login_url = reverse("login")
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f"{login_url}?next={self.url}")


class PrivateDishUpdateViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="user", password="password123"
        )
        self.client.force_login(self.user)

        self.dish_type = DishType.objects.create(name="Salad")
        self.new_dish_type = DishType.objects.create(name="Soup")

        self.ingredient = Ingredient.objects.create(name="Salt")
        self.new_ingredient = Ingredient.objects.create(name="Pepper")

        self.dish = Dish.objects.create(
            name="Caesar",
            price=10.5,
            description="desc",
            dish_type=self.dish_type
        )
        self.dish.ingredients.add(self.ingredient)

        self.url = reverse("kitchen:dish-update", args=[self.dish.id])

    def test_access_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "kitchen/dish_form.html")
        self.assertIn("form", response.context)
        self.assertEqual(response.context["form"].initial["name"], "Caesar")

    def test_update_valid_dish(self):
        data = {
            "name": "Greek",
            "price": 12.0,
            "description": "updated-desc",
            "dish_type": self.new_dish_type.id,
            "ingredients": [self.new_ingredient.id],
        }
        response = self.client.post(self.url, data)
        self.dish.refresh_from_db()

        self.assertEqual(self.dish.name, "Greek")
        self.assertEqual(self.dish.price, 12.0)
        self.assertEqual(self.dish.description, "updated-desc")
        self.assertEqual(self.dish.dish_type, self.new_dish_type)
        self.assertIn(self.new_ingredient, self.dish.ingredients.all())
        self.assertRedirects(response, reverse("kitchen:dish-list"))

    def test_update_invalid_dish(self):
        response = self.client.post(
            self.url,
            {"name": "", "dish_type": self.dish_type.id}
        )
        form = response.context["form"]
        self.assertTrue(form.errors)
        self.dish.refresh_from_db()
        self.assertEqual(self.dish.name, "Caesar")

    def test_update_nonexistent_dish_returns_404(self):
        bad_url = reverse("kitchen:dish-update", args=[999])
        response = self.client.get(bad_url)
        self.assertEqual(response.status_code, 404)


class PublicDishDeleteViewTests(TestCase):
    def setUp(self):
        self.dish_type = DishType.objects.create(name="Salad")
        self.dish = Dish.objects.create(
            name="Caesar",
            price=10.5,
            description="desc",
            dish_type=self.dish_type
        )
        self.url = reverse("kitchen:dish-delete", args=[self.dish.id])

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        login_url = reverse("login")
        self.assertRedirects(response, f"{login_url}?next={self.url}")


class PrivateDishDeleteViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="user", password="password123"
        )
        self.client.force_login(self.user)

        self.dish_type = DishType.objects.create(name="Salad")
        self.dish = Dish.objects.create(
            name="Caesar",
            price=10.5,
            description="desc",
            dish_type=self.dish_type
        )
        self.url = reverse("kitchen:dish-delete", args=[self.dish.id])

    def test_access_delete_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "kitchen/confirm_delete_dish.html")
        self.assertIn("object", response.context)
        self.assertEqual(response.context["object"], self.dish)

    def test_delete_dish(self):
        response = self.client.post(self.url)
        self.assertFalse(Dish.objects.filter(id=self.dish.id).exists())
        self.assertRedirects(response, reverse("kitchen:dish-list"))

    def test_delete_nonexistent_dish_returns_404(self):
        bad_url = reverse("kitchen:dish-delete", args=[999])
        response = self.client.get(bad_url)
        self.assertEqual(response.status_code, 404)
