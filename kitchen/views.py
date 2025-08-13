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


class CookDetailView(generic.DetailView):
    model = Cook


class DishListView(generic.ListView):
    model = Dish
    context_object_name = "dishes_list"

    def get_queryset(self):
        queryset = super().get_queryset()
        self.dish_type = None

        dish_type_id = self.request.GET.get("dish_type")
        if dish_type_id:
            queryset = queryset.filter(dish_type_id=dish_type_id)
            try:
                self.dish_type = DishType.objects.get(id=dish_type_id)
            except DishType.DoesNotExist:
                self.dish_type = None
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["selected_dish_type"] = self.dish_type
        return context


class DishDetailView(generic.DetailView):
    model = Dish
