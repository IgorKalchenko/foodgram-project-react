from django.db.models import Sum
from django.http import HttpResponse
from recipes.models import RecipeIngredient
from rest_framework import status
from rest_framework.response import Response


def download_cart(user):
    if not user.is_in_shopping_cart.exists():
        return Response(status=status.HTTP_400_BAD_REQUEST)
    ingredients = RecipeIngredient.objects.filter(
        recipe__in=(user.is_in_shopping_cart.values('id'))
    ).values(
        'ingredients__name',
        'ingredients__measurement_unit'
    ).annotate(amount=Sum('amount'))
    filename = f'{user.username}_shopping_list.txt'
    shopping_list = 'Shopping List\n\n'
    for ingredient in ingredients:
        name = ingredient['ingredients__name']
        amount = ingredient['amount']
        measurement_unit = ingredient['ingredients__measurement_unit']
        shopping_list += (
            f'{name}: {amount} {measurement_unit}\n'
        )
    return HttpResponse(
        shopping_list, headers={
            'Content-Type': 'text.txt; charset=utf-8',
            'Content-Disposition': f'attachment; filename={filename}'
        }
    )
