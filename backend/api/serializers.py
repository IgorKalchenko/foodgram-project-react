from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            RecipeTag, ShoppingCart, Tag)
from rest_framework import serializers
from users.models import Subscription

User = get_user_model()


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
        if user.is_anonymous or (user == obj):
            return False
        return Subscription.objects.filter(
            user=user, author=obj
        ).exists()


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


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        read_only_fields = '__all__',


class RecipeIngredientGetSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredients.id')
    name = serializers.CharField(source='ingredients.name')
    measurement_unit = serializers.CharField(
        source='ingredients.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientToRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(write_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
        read_only_fields = '__all__',


class RecipeGetSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    ingredients = RecipeIngredientGetSerializer(
        source='recipe_amount', many=True
    )
    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    author = CustomUserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'name', 'image', 'text', 'tags',
            'ingredients', 'cooking_time', 'is_favorited',
            'is_in_shopping_cart'
        )

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=user, recipe__id=obj.id
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=user, recipe__id=obj.id
        ).exists()


class RecipeShortSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = '__all__',


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    ingredients = IngredientToRecipeSerializer(many=True)
    tags = serializers.ListField(
        child=serializers.SlugRelatedField(
            slug_field='id',
            queryset=Tag.objects.all()
        ),
        allow_empty=False
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'image', 'text',
            'tags', 'ingredients', 'cooking_time'
        )

    def validate(self, data):
        if data['name'] == data['text']:
            raise serializers.ValidationError(
                'The value of "name" field could '
                'not be the same as the value of "text" field.'
            )
        if not data['tags']:
            raise serializers.ValidationError(
                '"Tag" field must be filled out.'
            )
        for tag in data['tags']:
            if data['tags'].count(tag) > 1:
                raise serializers.ValidationError(
                    f'You have repeated tags: {tag}'
                )
        if not data['ingredients']:
            raise serializers.ValidationError(
                '"Ingredients" field must be filled out.'
            )
        for ingredient in data['ingredients']:
            if data['ingredients'].count(ingredient) > 1:
                raise serializers.ValidationError(
                    f'You have repeated ingredients: {ingredient}'
                )
        return data

    @classmethod
    def recipe_ingredient_create(cls, recipe, ingredients):
        recipe_list = [RecipeIngredient(
            recipe=recipe,
            ingredients=get_object_or_404(Ingredient, id=ingredient['id']),
            amount=ingredient['amount']
        ) for ingredient in ingredients]
        RecipeIngredient.objects.bulk_create(recipe_list)

    def to_representation(self, value):
        return RecipeGetSerializer(value, context=self.context).data

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=self.context.get('request').user,
            **validated_data
        )
        self.recipe_ingredient_create(
            recipe=recipe,
            ingredients=ingredients
        )
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        ingredients = self.context['request'].data['ingredients']
        tags = self.context['request'].data['tags']
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.save()
        if tags:
            RecipeTag.objects.filter(recipe=instance).delete()
            instance.tags.clear()
            instance.tags.set(tags)
        if ingredients:
            RecipeIngredient.objects.filter(recipe=instance).delete()
            instance.ingredients.clear()
            self.recipe_ingredient_create(
                recipe=instance,
                ingredients=ingredients
            )
        return instance


class SubscriptionSerializer(CustomUserSerializer):
    recipes = RecipeShortSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()

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
        read_only_fields = '__all__',

    def get_recipes_count(self, obj):
        return obj.recipes.count()
