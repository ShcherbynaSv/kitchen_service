from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from kitchen.models import DishType, Ingredient, Dish, Cook


@admin.register(Cook)
class CookAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ("years_of_experience",)
    list_filter = UserAdmin.list_filter + ("years_of_experience",)
    fieldsets = UserAdmin.fieldsets + (
        ("Additional info", {"fields": ("years_of_experience",)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Additional info",
            {"fields": (
                "first_name",
                "last_name",
                "is_staff",
                "years_of_experience",
            )}
        ),
    )


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ["name", "description", "price", "dish_type"]
    list_filter = ["name", "price", "dish_type"]
    search_fields = ["name"]


admin.site.register(DishType)
admin.site.register(Ingredient)
