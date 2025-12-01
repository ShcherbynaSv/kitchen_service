from django.test import TestCase
from django.contrib.auth import get_user_model

from kitchen.forms import (
    CookCreationForm,
    CookUpdateForm,
    DishForm,
    DishTypeSearchForm,
    IngredientSearchForm,
    DishSearchForm,
    CookSearchForm,
)
from kitchen.models import Cook, Dish, Ingredient, DishType


class CookCreationFormTests(TestCase):
    def test_valid_data(self):
        form = CookCreationForm(
            data={
                "username": "test_user",
                "password1": "StrongPass123",
                "password2": "StrongPass123",
                "first_name": "John",
                "last_name": "Doe",
                "years_of_experience": 5,
            }
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_missing_required_fields(self):
        form = CookCreationForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)
        self.assertIn("password1", form.errors)


class CookUpdateFormTests(TestCase):
    def setUp(self):
        self.cook = get_user_model().objects.create_user(
            username="old_user", password="test12345", years_of_experience=3
        )

    def test_update_valid(self):
        form = CookUpdateForm(
            data={
                "username": "new_user",
                "first_name": "Test",
                "last_name": "User",
                "email": "test@example.com",
                "years_of_experience": 10,
            },
            instance=self.cook,
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_missing_username(self):
        form = CookUpdateForm(data={}, instance=self.cook)
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)


class DishFormTests(TestCase):
    def setUp(self):
        self.cook1 = get_user_model().objects.create_user(
            username="c1", password="pass"
        )
        self.cook2 = get_user_model().objects.create_user(
            username="c2", password="pass"
        )

        self.ing1 = Ingredient.objects.create(name="Salt")
        self.ing2 = Ingredient.objects.create(name="Pepper")

        self.dish_type = DishType.objects.create(name="Main")

    def test_valid_dish(self):
        form = DishForm(
            data={
                "name": "Soup",
                "description": "Hot soup",
                "price": 10,
                "dish_type": self.dish_type.id,
                "cooks": [self.cook1.id, self.cook2.id],
                "ingredients": [self.ing1.id, self.ing2.id],
            }
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_optional_fields(self):
        form = DishForm(
            data={
                "name": "Soup",
                "description": "Hot soup",
                "price": 10,
            }
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_missing_required(self):
        form = DishForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)
        self.assertIn("description", form.errors)
        self.assertIn("price", form.errors)


class SearchFormTests(TestCase):
    def test_dish_type_search_form(self):
        form = DishTypeSearchForm(data={"name": "Sou"})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["name"], "Sou")

    def test_ingredient_search_form(self):
        form = IngredientSearchForm(data={"name": "Pep"})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["name"], "Pep")

    def test_dish_search_form(self):
        form = DishSearchForm(data={"name": "Lasag"})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["name"], "Lasag")

    def test_cook_search_form(self):
        form = CookSearchForm(data={"full_name": "John Doe"})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["full_name"], "John Doe")
