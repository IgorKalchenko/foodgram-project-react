from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import Ingredient, Recipe, RecipeIngredient, RecipeTag, Tag

User = get_user_model()


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        read_only_fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
        read_only_fields = ('id', 'name', 'color', 'slug')


class RecipeGetSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    ingredients = IngredientSerializer(many=True)
    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'name', 'image', 'text', 'tags',
            'ingredients', 'cooking_time', 'is_favorited',
            'is_in_shopping_cart'
        )

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous or user == obj:
            return False
        return user.is_favorited.filter(id=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous or user == obj:
            return False
        return user.is_in_shopping_cart.filter(id=obj.id).exists()


class RecipeShortSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = '__all__'


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    ingredients = IngredientSerializer(many=True)
    tags = TagSerializer(many=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'name', 'image', 'text',
            'tags', 'ingredients', 'cooking_time'
        )

    @classmethod
    def recipe_ingredient_create(self, recipe, ingredients):
        for ingredient in ingredients:
            RecipeIngredient.objects.get_or_create(
                recipe=recipe,
                ingredients=ingredient['id'],
                amount=ingredient['amount']
            )

    def create(self, validated_data):
        ingredients = validated_data.get('ingredients')
        tags = validated_data.get('tags')
        amount = validated_data.get('amount')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient, tag in ingredients, tags:
            current_ingredient = Ingredient.objects.get(id=ingredient.id)
            current_tag = Ingredient.objects.get(id=tag.id)
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=current_ingredient,
                amount=amount
            )
            RecipeTag.objects.create(recipe=recipe, tag=current_tag)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.get('ingredients')
        tags = validated_data.get('tags')
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.tags = validated_data.get('tags', instance.tags)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        if tags:
            for tag in tags:
                RecipeTag.objects.create(
                    recipe=instance.id,
                    tag=tag.id
                )
        if ingredients:
            for ingredient in ingredients:
                RecipeIngredient.objects.get_or_create(
                    recipe=instance.id,
                    ingredients=ingredient.id,
                    amount=ingredient.amount
                )


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous or user == obj:
            return False
        return user.is_subscribed.filter(id=obj.id).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Value "me" is forbidden for username.'
            )
        return value


class SubscriptionSerializer(CustomUserSerializer):
    """
    Сериализатор для вывода авторов, на которых подписан текущий пользователь.
    """
    recipes = RecipeShortSerializer(many=True, source='recipes')
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        read_only_fields = '__all__'

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous or user == obj:
            return False
        return user.is_subscribed.filter(id=obj.id).exists()
