from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag, RecipeTag)

User = get_user_model()


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient


class RecipeTagInline(admin.TabularInline):
    model = RecipeTag


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    list_filter = ('author', 'name', 'tags')
    search_fields = ('author', 'name', 'tags')
    read_only_fields = ('favorite_score',)
    inlines = (RecipeIngredientInline, RecipeTagInline)

    def favorite_score(self, obj):
        return User.objects.filter(is_favorited=obj).count()


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)


class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredients', 'amount')
    list_filter = ('recipe', 'ingredients')


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    list_filter = ('name', 'slug')


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_filter = ('user', 'recipe')


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_filter = ('user', 'recipe')


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Favorite, FavoriteAdmin)
