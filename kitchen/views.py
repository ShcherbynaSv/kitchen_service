from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic

from kitchen.forms import (
    CookUpdateForm,
    CookCreationForm,
    DishForm,
    DishTypeSearchForm,
    IngredientSearchForm,
    CookSearchForm,
    DishSearchForm
)
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

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(DishTypeListView, self).get_context_data(**kwargs)
        name = self.request.GET.get("name", "")
        context["search_form"] = DishTypeSearchForm(initial={"name": name})
        return context

    def get_queryset(self):
        queryset = DishType.objects.all()
        form = DishTypeSearchForm(self.request.GET)
        if form.is_valid():
            return queryset.filter(name__icontains=form.cleaned_data["name"])
        return queryset


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

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(IngredientListView, self).get_context_data(**kwargs)
        name = self.request.GET.get("name", "")
        context["search_form"] = IngredientSearchForm(initial={"name": name})
        return context

    def get_queryset(self):
        queryset = Ingredient.objects.all()
        form = IngredientSearchForm(self.request.GET)
        if form.is_valid():
            return queryset.filter(name__icontains=form.cleaned_data["name"])
        return queryset


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

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(CookListView, self).get_context_data(**kwargs)
        full_name = self.request.GET.get("full_name")
        search_form = CookSearchForm(
            initial={"full_name": full_name}
        )
        context["search_form"] = search_form
        return context

    def get_queryset(self):
        queryset = Cook.objects.all()
        form = CookSearchForm(self.request.GET)
        if form.is_valid():
            query = form.cleaned_data.get("full_name")
            if query:
                parts = query.strip().split()
                if len(parts) == 2:
                    first, second = parts
                    queryset = (
                        queryset.filter(
                            first_name__icontains=first,
                            last_name__icontains=second
                        )
                        | queryset.filter(
                            first_name__icontains=second,
                            last_name__icontains=first
                        )
                    )
                else:
                    queryset = (
                        queryset.filter(first_name__icontains=query)
                        | queryset.filter(last_name__icontains=query)
                    )
        return queryset


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
        queryset = (queryset.select_related("dish_type")
                    .prefetch_related("ingredients"))
        ingredient_id = self.request.GET.get("ingredients")
        self.ingredient = Ingredient.objects.filter(id=ingredient_id).first() \
            if ingredient_id else None
        if self.ingredient:
            queryset = queryset.filter(ingredients=self.ingredient)

        dish_type_id = self.request.GET.get("dish_type")
        self.dish_type = DishType.objects.filter(id=dish_type_id).first() \
            if dish_type_id else None
        if self.dish_type:
            queryset = queryset.filter(dish_type=self.dish_type)

        self.search_form = DishSearchForm(
            self.request.GET or None,
            initial={"name": self.request.GET.get("name", "")}
        )
        if self.search_form.is_valid():
            query = self.search_form.cleaned_data.get("name")
            if query:
                queryset = queryset.filter(name__icontains=query)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "selected_dish_type": self.dish_type,
            "selected_ingredient": self.ingredient,
            "search_form": self.search_form,
        })
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
