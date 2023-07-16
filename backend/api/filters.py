from django.contrib.auth import get_user_model
from django_filters import rest_framework as filters
from recipes.models import Recipe, Tag

User = get_user_model()


class RecipeFilter(filters.FilterSet):

    tags = filters.filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug'
    )

    author = filters.ModelChoiceFilter(queryset=User.objects.all())

    is_favorited = filters.BooleanFilter(
        field_name='is_favorited',
        method='filter_favorited',
    )

    is_in_shopping_cart = filters.BooleanFilter(
        field_name='is_in_shopping_cart',
        method='filter_shopping_cart',
    )

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        if self.request.user.is_anonymous:
            return queryset.exclude(is_private=True)
        return queryset

    def filter_favorited(self, queryset, name, value):
        if self.request.user.is_anonymous:
            return queryset.none()
        if value:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def filter_shopping_cart(self, queryset, name, value):
        if self.request.user.is_anonymous:
            return queryset.none()
        if value:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ('author', 'tags',)
