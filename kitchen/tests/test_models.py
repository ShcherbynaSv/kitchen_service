from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from kitchen.models import DishType, Ingredient, Dish


class ModelsTests(TestCase):
    def setUp(self):
        self.dish_type = DishType.objects.create(name="test-dish_type")
        self.ingredient = Ingredient.objects.create(name="test-ingredient")
        self.username = "test-username"
        self.password = "test-password_1234"
        self.cook = get_user_model().objects.create_user(
            username=self.username,
            password=self.password
        )
        self.dish = Dish.objects.create(
            name="test-name",
            description="test-description",
            price=10.55,
            dish_type=self.dish_type
        )
        self.dish.ingredients.set([self.ingredient])
        self.dish.cooks.set([self.cook])

    def test_dish_type_str(self):
        self.assertEqual(str(self.dish_type), self.dish_type.name)

    def test_ingredient_str(self):
        self.assertEqual(str(self.ingredient), self.ingredient.name)

    def test_cook_with_years_of_experience(self):
        self.cook.years_of_experience = 10
        self.assertEqual(self.cook.username, self.username)
        self.assertTrue(self.cook.check_password(self.password))
        self.assertEqual(self.cook.years_of_experience, 10)

    def test_cook_get_absolute_url(self):
        expected_url = reverse("kitchen:cook-detail", args=[str(self.cook.id)])
        self.assertEqual(self.cook.get_absolute_url(), expected_url)

    def test_dish_str(self):
        self.assertEqual(str(self.dish), self.dish.name)

    def test_dish_get_absolute_url(self):
        expected_url = reverse("kitchen:dish-detail", args=[str(self.dish.id)])
        self.assertEqual(self.dish.get_absolute_url(), expected_url)
