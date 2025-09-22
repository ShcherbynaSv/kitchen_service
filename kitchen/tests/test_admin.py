from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib import admin
from django.utils import timezone

from kitchen.admin import CookAdmin, DishAdmin
from kitchen.models import Dish, DishType, Cook


class AdminSiteTests(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            username="admin",
            password="admin1234"
        )
        self.client.force_login(self.admin_user)

        self.cook = get_user_model().objects.create_user(
            username="test-cook",
            password="cook-1234",
            years_of_experience=10
        )
        self.dish_type = DishType.objects.create(name="test_dish_type")
        self.dish = Dish.objects.create(
            name="test-dish",
            description="test-dish-description",
            price=10.55,
            dish_type=self.dish_type
        )

    def test_cook_list_display(self):
        url = reverse("admin:kitchen_cook_changelist")
        res = self.client.get(url)

        self.assertContains(res, str(self.cook.years_of_experience))

    def test_cook_list_filter(self):
        model_admin = CookAdmin(Cook, admin.site)
        self.assertEqual(
            model_admin.list_filter,
            (
                "is_staff",
                "is_superuser",
                "is_active",
                "groups",
                "years_of_experience"
            )
        )

    def test_cook_fieldsets_contains_additional_info(self):
        model_admin = CookAdmin(Cook, admin.site)
        fieldsets = dict(model_admin.fieldsets)
        self.assertIn("Additional info", fieldsets)
        self.assertIn(
            "years_of_experience",
            fieldsets["Additional info"]["fields"]
        )

    def test_ook_add_fieldsets_contains_additional_info(self):
        model_admin = CookAdmin(Cook, admin.site)
        add_fieldsets = dict(model_admin.add_fieldsets)
        self.assertIn("Additional info", add_fieldsets)
        self.assertIn("first_name", add_fieldsets["Additional info"]["fields"])
        self.assertIn("last_name", add_fieldsets["Additional info"]["fields"])
        self.assertIn("is_staff", add_fieldsets["Additional info"]["fields"])
        self.assertIn(
            "years_of_experience",
            add_fieldsets["Additional info"]["fields"]
        )

    def test_dish_list_display(self):
        url = reverse("admin:kitchen_dish_changelist")
        res = self.client.get(url)

        self.assertContains(res, self.dish.name)
        self.assertContains(res, self.dish.description)
        self.assertContains(res, self.dish.price)
        self.assertContains(res, str(self.dish.dish_type))

    def test_dish_list_filter(self):
        model_admin = DishAdmin(Dish, admin.site)
        self.assertEqual(
            model_admin.list_filter,
            ["name", "price", "dish_type"]
        )

    def test_dish_search_fields(self):
        model_admin = DishAdmin(Dish, admin.site)
        self.assertEqual(model_admin.search_fields, ["name"])
