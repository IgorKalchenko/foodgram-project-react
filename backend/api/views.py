from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from users.models import Subscription

from .filters import IngredientFilter, RecipeFilter
from .paginators import PageLimitPagination
from .permissions import AuthorOrReadOnly
from .serializers import (CustomUserCreateSerializer, CustomUserSerializer,
                          IngredientSerializer, RecipeCreateUpdateSerializer,
                          RecipeGetSerializer, RecipeShortSerializer,
                          SubscriptionSerializer, TagSerializer)
from .services import download_cart

User = get_user_model()


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all().order_by('name')
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all().order_by('name')
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]
    filter_backends = (IngredientFilter,)
    search_fields = ('^name',)
    pagination_class = None


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
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

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
        elif request.method == 'DELETE':
            if current_object.exists():
                current_object.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'It\'s not added'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=True,
        permission_classes=(IsAuthenticated,),
        methods=['post', 'delete']
    )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        return self.add_or_delete_object(
            Favorite, recipe=recipe, request=request
        )

    @action(
        detail=True,
        permission_classes=(IsAuthenticated,),
        methods=['post', 'delete']
    )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        return self.add_or_delete_object(
            ShoppingCart, recipe=recipe, request=request
        )

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        user = request.user
        return download_cart(user=user)
