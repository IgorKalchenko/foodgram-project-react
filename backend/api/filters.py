from django_filters.rest_framework import FilterSet
from django_filters.rest_framework.filters import (ModelMultipleChoiceFilter,
                                                   NumberFilter)
from recipes.models import Recipe, Tag
from rest_framework.filters import SearchFilter


class RecipeFilter(FilterSet):
    """
    Filter for Recipes.
    """
    is_favorited = NumberFilter(method='filter_is_favorited')
    is_in_shopping_cart = NumberFilter(method='filter_is_in_shopping_cart')
    tags = ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug'
    )
    author = NumberFilter()

    def filter_is_favorited(self, queryset, name, value):
        if value and not self.request.user.is_anonymous:
            return queryset.filter(is_favorited__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value and not self.request.user.is_anonymous:
            return queryset.filter(is_in_shopping_cart__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')


class IngredientFilter(SearchFilter):
    """
    Filter for Ingredients.
    """
    search_param = 'name'
