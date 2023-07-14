from typing import Type, Tuple, Any, Dict

from api.serializers import RecipeListSerializer
from django.db import models
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from recipes.models import Recipe
from rest_framework import status


def create_shopping_list(queryset):
    """
    Эта функция создает список покупок на основе переданного QuerySet.
    QuerySet должен представлять собой список объектов
     из модели RecipeIngredient.
    Каждый элемент списка имеет следующий формат:
    'Название ингредиента (единицы): количество'.
    """
    data = {}

    for ingr in queryset:
        key = f'{ingr.ingredient.name} ({ingr.ingredient.measurement_unit})'
        data.setdefault(key, 0)
        data[key] += ingr.amount

    shopping_list = ['Список покупок:\n']

    for key, value in data.items():
        item = f'- {key}: {value} \n'
        shopping_list.append(item)

    return shopping_list


def modify_obj(
        request: HttpRequest,
        pk: int,
        model: Type[models.Model],
        create: bool,
) -> Tuple[Dict[str, Any], int]:
    """
    Функция для RecipeViewSet.
    Создает или удаляет связь между рецептом и пользователем через модель.

    Параметры:
    - request: запрос
    - pk: id рецепта
    - model: промежуточная модель для создания связи с рецептом
    - create: флаг, указывающий на создание или удаление связи

    Возвращает кортеж из двух элементов:
    - подготовленные данные для ответа
    - статус ответа
    """
    recipe = get_object_or_404(Recipe, pk=pk)
    try:
        if create:
            model.objects.create(recipe=recipe, user=request.user)
            serializer = RecipeListSerializer(recipe, context={'request': request})
            return serializer.data, status.HTTP_201_CREATED
        else:
            model.objects.get(recipe=recipe, user=request.user).delete()
            return (
                {"success": f"Рецепт с id {pk} удален."},
                status.HTTP_204_NO_CONTENT,
            )
    except models.ObjectDoesNotExist:
        return (
            {"errors": f"У вас нет рецепта с id {pk}."},
            status.HTTP_400_BAD_REQUEST,
        )
