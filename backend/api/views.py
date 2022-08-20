from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import (AllowAny, IsAuthenticated)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .filters import RecipeFilter
from .paginators import PageLimitPagination
from .permissions import AuthorOrReadOnly
from .serializers import (CustomUserSerializer, IngredientSerializer,
                          RecipeCreateUpdateSerializer, RecipeGetSerializer,
                          RecipeShortSerializer, SubscriptionSerializer,
                          TagSerializer, CustomUserCreateSerializer)
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.models import Subscription

User = get_user_model()


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all().order_by('name')
    serializer_class = TagSerializer
    permission_classes = [AllowAny]


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all().order_by('name')
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]
    filter_backends = (SearchFilter,)
    search_fields = ('^name',)


class CustomUserViewSet(UserViewSet):
    pagination_class = PageLimitPagination
    serializer_class = CustomUserCreateSerializer

    @action(
        detail=True,
        permission_classes=[IsAuthenticated],
        methods=['post', 'delete']
    )
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)
        subscription = Subscription.objects.filter(
            user=user, is_subscribed=author
        )
        if request.method == 'POST':
            if user == author:
                return Response(
                    {'errors': 'It\'s not allowed to subscribe to yourself.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            elif subscription.exists():
                return Response(
                    {'errors': 'You are already subscribed to the user'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Subscription.objects.create(
                user=user, is_subscribed=author
            )
            serializer = CustomUserSerializer(
                author, context={'request': request}
            )
            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )
        if not subscription.exists():
            return Response(
                {'errors': 'You are not subscribed to the user'},
                status=status.HTTP_400_BAD_REQUEST
            )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        queryset = User.objects.filter(
            subscribed_to__user=request.user
        ).order_by('subscribed_to')
        page = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all().order_by('-pub_date')
    permission_classes = (AuthorOrReadOnly,)
    pagination_class = PageLimitPagination
    filter_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RecipeCreateUpdateSerializer
        return RecipeGetSerializer

    @staticmethod
    def add_or_delete_object(model, recipe, request):
        current_object = model.objects.filter(
            user=request.user, recipe=recipe
        )
        if request.method == 'POST':
            if current_object.exists():
                return Response(
                    {'errors': 'It\'s already added'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            model.objects.create(user=request.user, recipe=recipe)
            serializer = RecipeShortSerializer(recipe)
            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )
        current_object.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        permission_classes=(IsAuthenticated,),
        methods=['post', 'delete']
    )
    def favorite(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        return self.add_or_delete_object(
            Favorite, recipe=recipe, request=request
        )

    @action(
        detail=True,
        permission_classes=(IsAuthenticated,),
        methods=['post', 'delete']
    )
    def shopping_cart(self, request, id):
        recipe = get_object_or_404(Recipe, id=id)
        return self.add_or_delete_object(
            ShoppingCart, recipe=recipe, request=request
        )

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        user = self.request.user
        if not user.is_in_shopping_cart.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        ingredients = RecipeIngredient.objects.filter(
            recipe__in=(user.is_in_shopping_cart.values('id'))
        ).values(
            'ingredient__name',
            'ingredients__measurement_unit'
        ).annotate(amount=Sum('amount'))

        filename = f'{user.username}_shopping_list.txt'
        shopping_list = 'Shopping List\n\n'
        for ingredient in ingredients:
            name = ingredient['ingredient__name']
            amount = ingredient['amount']
            measurement_unit = ingredient['ingredient__measurement_unit']
            shopping_list += (
                f'{name}: {amount} {measurement_unit}\n'
            )
        response = HttpResponse(
            shopping_list, headers={
                'Content-Type': 'text.txt; charset=utf-8',
                'Content-Disposition': f'attachment; filename={filename}'
            }
        )
        return response
