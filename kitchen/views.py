from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from kitchen.models import DishType, Ingredient, Cook, Dish


def index(request: HttpRequest) -> HttpResponse:
    context = {
        "dish_types": DishType.objects.all().count(),
        "ingredients": Ingredient.objects.all().count(),
        "cooks": Cook.objects.all().count(),
        "dishes": Dish.objects.all().count(),
    }
    return render(request, "kitchen/index.html", context=context)
