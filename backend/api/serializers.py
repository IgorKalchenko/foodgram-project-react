from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from rest_framework import serializers

User = get_user_model()


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        read_only_fields = ('id', 'name', 'measurement_unit')


class IngredientToRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


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
    ingredients = IngredientToRecipeSerializer(many=True)
    tags = serializers.ListField(
        child=serializers.SlugRelatedField(
            slug_field='id',
            queryset=Tag.objects.all(),
            many=True
        ),
        allow_empty=False
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'name', 'image', 'text',
            'tags', 'ingredients', 'cooking_time'
        )

    def validate(self, data):
        if data['name'] == data['text']:
            raise serializers.ValidationError(
                'The value of "name" field could '
                'not be the same as the value of "text" field.'
            )
        if self.context.get('request').method == 'POST':
            if Recipe.objects.filter(
                author=data['author'],
                name=data['name']
            ).exists():
                return serializers.ValidationError(
                    'You\'ve already created the recipe with this name.'
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
    def recipe_ingredient_tag_create(cls, recipe, tags, ingredients):
        recipe_list = [RecipeIngredient(
            recipe=recipe,
            ingredients=get_object_or_404(Ingredient, id=ingredient.id),
            amount=ingredient['amount']
        ) for ingredient in ingredients]
        RecipeIngredient.objects.bulk_create(recipe_list)
        recipe.tags.set(tags)

    def create(self, validated_data):
        ingredients = validated_data.get('ingredients')
        tags = validated_data.get('tags')
        recipe = Recipe.objects.create(**validated_data)
        self.recipe_ingredient_tag_create(
            recipe=recipe,
            tags=tags,
            ingredients=ingredients
        )
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
        instance.ingredients.clear()
        self.recipe_ingredient_tag_create(
            recipe=instance,
            tags=tags,
            ingredients=ingredients
        )
        instance.save()
        return instance


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
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source='recipes.count'
    )

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

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous or user == obj:
            return False
        return user.is_subscribed.filter(id=obj.id).exists()
