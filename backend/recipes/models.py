from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения'
    )

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        blank=False,
        verbose_name='Название'
    )
    color = models.CharField(
        max_length=7,
        null=True,
        blank=False,
        unique=True,
        verbose_name='Цвет в HEX'
    )
    slug = models.SlugField(
        max_length=200,
        null=True,
        blank=False,
        unique=True,
        verbose_name='Уникальный слаг'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        blank=False,
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    name = models.CharField(
        max_length=200,
        blank=False,
        verbose_name='Название',
        help_text='Название рецепта'
    )
    image = models.ImageField(
        verbose_name=_('Image'),
        blank=False,
        help_text='Изображение для рецепта',
        upload_to='recipes/'
    )
    text = models.TextField(
        verbose_name=_('Text'),
        blank=False,
        help_text='Текст рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        blank=False,
        related_name='recipes',
        verbose_name=_('Ingredients')
    )
    tags = models.ManyToManyField(
        Tag,
        through='RecipeTag',
        blank=False,
        related_name='recipes',
        verbose_name=_('Tags')
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления',
        blank=False,
        help_text='Время приготовления в минутах',
        validators=(MinValueValidator(1),)
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        blank=False,
        auto_now_add=True
    )

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name='recipe_amount',
        blank=False,
        on_delete=models.CASCADE)
    ingredients = models.ForeignKey(
        Ingredient,
        related_name='ingredients_amount',
        blank=False,
        on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(
        verbose_name=_('amount'),
        blank=False,
        validators=(MinValueValidator(1),)
    )

    def __str__(self):
        return f'{self.recipe} {self.ingredients}'

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['ingredients', 'recipe'],
                name='ingredient_constraints'
            )
        ]


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        blank=False
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        blank=False
    )

    def __str__(self):
        return f'{self.recipe} {self.tag}'

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['tag', 'recipe'],
                name='tag_constraints'
            )
        ]


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='is_in_shopping_cart',
        verbose_name=_('user')
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='is_in_shopping_cart',
        verbose_name=_('recipe')
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='shopping_cart_constraints'
            )
        ]


class Favorite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='is_favorited',
        verbose_name=_('user')
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='is_favorited',
        verbose_name=_('recipe')
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='favorite_constraints'
            )
        ]
