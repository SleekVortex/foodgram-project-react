from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        'Имя тега',
        max_length=200,
        unique=True
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        null=True,
        db_index=True
    )
    color = models.CharField(
        'Цвет',
        max_length=7,
        null=True,
        unique=False
    )

    def get_absolute_url(self):
        return reverse('tag-detail', kwargs={'tag_id': self.pk})

    def __str__(self):
        return f'Тег:{self.name}'

    class Meta:
        ordering = ['name']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Ingredient(models.Model):
    name = models.CharField(
        'Название',
        max_length=100,
    )
    measurement_unit = models.CharField(
        'Единицы измерения',
        max_length=100,
    )

    def get_absolute_url(self):
        return reverse('ingredient-detail', args=self.pk)

    def __str__(self):
        return (
            f'Название:{self.name}.'
            f' Единицы измерения:({self.measurement_unit})'
        )

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Recipe(models.Model):
    name = models.CharField(
        'Название',
        max_length=200
    )
    text = models.TextField(
        'Описание',
        max_length=1000
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
    )
    image = models.ImageField(
        'Изображение',
        upload_to='images/',
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=[MinValueValidator(
            1,
            message='Время приготовления не может быть меннее 1 минуты.')],
    )
    tags = models.ManyToManyField('Tag')
    ingredients = models.ManyToManyField(
        'Ingredient',
        through='RecipeIngredient',
    )
    created = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
    )

    def get_absolute_url(self):
        return reverse(
            'recipe-detail',
            kwargs={'recipe_id': self.pk},
        )

    def __str__(self):
        return f'Название: {self.name}'

    class Meta:
        ordering = ['-id', 'name']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'author'],
                name='unique_recipe_author'
            )
        ]
        unique_together = ['name', 'author']


class Favorite(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites'
    )

    def __str__(self):
        return f'Пользователь: {self.user}. Рецепт: {self.recipe}.'

    class Meta:
        ordering = ['recipe', 'user']
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_user_favorite_recipe')
        ]
        unique_together = ['user', 'recipe']


class ShoppingCart(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart'
    )

    def __str__(self):
        return f'Пользователь: {self.user}. Рецепт: {self.recipe}.'

    class Meta:
        ordering = ['recipe', 'user']
        verbose_name = 'Рецепт в корзине'
        verbose_name_plural = 'Рецепты в корзине'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_user_recipe_in_cart')
        ]
        unique_together = ['user', 'recipe']


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[MinValueValidator(
            1,
            message='Количество не должно быть менее 1.',
        )]
    )

    def __str__(self):
        return f'Рецепт:{self.recipe}. Ингредиент:{self.ingredient}.'

    class Meta:
        ordering = ['recipe__name']
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_ingredient_recipe'
            )
        ]
        unique_together = ['ingredient', 'recipe']


class Subscription(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='subscription',
    )
    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
        related_name='subscriber',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'subscriber'], name='unique_subscriptions'
            )
        ]
        unique_together = ['author', 'subscriber']

    def __str__(self):
        return (
            f'Пользователь {self.subscriber.username} - '
            f'подписчик автора: {self.author.username}'
        )
