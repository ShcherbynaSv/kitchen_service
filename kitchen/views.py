from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import generic

from kitchen.models import DishType, Ingredient, Cook, Dish


def index(request: HttpRequest) -> HttpResponse:
    context = {
        "dish_types": DishType.objects.all().count(),
        "ingredients": Ingredient.objects.all().count(),
        "cooks": Cook.objects.all().count(),
        "dishes": Dish.objects.all().count(),
    }
    return render(request, "kitchen/index.html", context=context)


class DishTypeListView(generic.ListView):
    model = DishType
    template_name = "kitchen/dish_type_list.html"
    context_object_name = "dish_type_list"


class IngredientListView(generic.ListView):
    model = Ingredient


class CookListView(generic.ListView):
    model = Cook


class DishListView(generic.ListView):
    model = Dish
    context_object_name = "dishes_list"
