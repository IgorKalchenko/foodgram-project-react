from django_filters.rest_framework import FilterSet
from django_filters.rest_framework.filters import (AllValuesMultipleFilter,
                                                   NumberFilter)
from rest_framework.filters import SearchFilter
from recipes.models import Recipe


class RecipeFilter(FilterSet):
    """
    Filter for Recipes.
    """
    is_favorited = NumberFilter(method='get_is_favorited')
    is_in_shopping_cart = NumberFilter(method='get_is_in_shopping_cart')
    tags = AllValuesMultipleFilter(field_name='tags__slug')
    author = AllValuesMultipleFilter(field_name='author__username')

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')


class IngredientFilter(SearchFilter):
    """
    Filter for Ingredients.
    """
    search_param = 'name'

