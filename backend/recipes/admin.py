from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import Ingredient, Recipe

User = get_user_model()


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    list_filter = ('author', 'name', 'tags')
    readonly_fields = ('favorite_score',)

    def favorite_score(self, obj):
        return User.objects.filter(is_favorited=obj).count()


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
