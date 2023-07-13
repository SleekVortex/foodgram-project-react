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

