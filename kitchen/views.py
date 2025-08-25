from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic

from kitchen.forms import CookUpdateForm, CookCreationForm, DishForm
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
    paginate_by = 10


class DishTypeCreateView(LoginRequiredMixin, generic.CreateView):
    model = DishType
    fields = "__all__"
    success_url = reverse_lazy("kitchen:dish-type-list")
    template_name = "kitchen/dish_type_form.html"


class DishTypeUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = DishType
    fields = "__all__"
    success_url = reverse_lazy("kitchen:dish-type-list")
    template_name = "kitchen/dish_type_form.html"


class DishTypeDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = DishType
    template_name = "kitchen/confirm_delete_dish_type.html"
    success_url = reverse_lazy("kitchen:dish-type-list")


class IngredientListView(generic.ListView):
    model = Ingredient
    paginate_by = 10


class IngredientCreateView(LoginRequiredMixin, generic.CreateView):
    model = Ingredient
    fields = "__all__"
    success_url = reverse_lazy("kitchen:ingredient-list")
    template_name = "kitchen/ingredient_form.html"


class IngredientUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Ingredient
    fields = "__all__"
    success_url = reverse_lazy("kitchen:ingredient-list")
    template_name = "kitchen/ingredient_form.html"


class IngredientDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Ingredient
    success_url = reverse_lazy("kitchen:ingredient-list")
    template_name = "kitchen/confirm_delete_ingredient.html"


class CookListView(generic.ListView):
    model = Cook
    paginate_by = 10


class CookDetailView(generic.DetailView):
    model = Cook


class CookCreateView(LoginRequiredMixin, generic.CreateView):
    model = Cook
    form_class = CookCreationForm
    success_url = reverse_lazy("kitchen:cook-list")
    template_name = "kitchen/cook_form.html"


class CookUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Cook
    form_class = CookUpdateForm
    template_name = "kitchen/cook_form.html"

    def get_success_url(self):
        return reverse_lazy(
            "kitchen:cook-detail",
            kwargs={"pk": self.object.pk}
        )


class CookDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Cook
    success_url = reverse_lazy("kitchen:cook-list")
    template_name = "kitchen/confirm_delete_cook.html"


class DishListView(generic.ListView):
    model = Dish
    context_object_name = "dishes_list"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        self.dish_type = None
        self.ingredient = None

        dish_type_id = self.request.GET.get("dish_type")
        if dish_type_id:
            queryset = queryset.filter(dish_type_id=dish_type_id)
            try:
                self.dish_type = DishType.objects.get(id=dish_type_id)
            except DishType.DoesNotExist:
                self.dish_type = None

        ingredient_id = self.request.GET.get("ingredient")
        if ingredient_id:
            queryset = queryset.filter(ingredients__id=ingredient_id)
            try:
                self.ingredient = Ingredient.objects.get(id=ingredient_id)
            except Ingredient.DoesNotExist:
                self.ingredient = None

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["selected_dish_type"] = self.dish_type
        context["selected_ingredient"] = self.ingredient
        return context


class DishDetailView(generic.DetailView):
    model = Dish

    def get_queryset(self):
        return (
            super().get_queryset()
            .select_related("dish_type")
            .prefetch_related("cooks", "ingredients")
        )


class DishCreateView(LoginRequiredMixin, generic.CreateView):
    model = Dish
    form_class = DishForm
    success_url = reverse_lazy("kitchen:dish-list")
    template_name = "kitchen/dish_form.html"


class DishUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Dish
    form_class = DishForm
    success_url = reverse_lazy("kitchen:dish-list")
    template_name = "kitchen/dish_form.html"


class DishDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Dish
    success_url = reverse_lazy("kitchen:dish-list")
    template_name = "kitchen/confirm_delete_dish.html"
