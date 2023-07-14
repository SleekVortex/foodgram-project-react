from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (Favorite,
                            Ingredient,
                            Recipe,
                            RecipeIngredient,
                            ShoppingCart,
                            Tag
                            )
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import RecipeFilter
from .permissions import OwnerOrReadOnly, ReadOnly
from .serializers import (IngredientSerializer,
                          RecipeSerializer,
                          TagSerializer
                          )
from .utils import create_shopping_list, modify_obj

User = get_user_model()


class ReadOnlyViewSetBase(viewsets.ReadOnlyModelViewSet):
    permission_classes = (ReadOnly,)
    pagination_class = None
    http_method_names = ['get', ]


class TagViewSet(ReadOnlyViewSetBase):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(ReadOnlyViewSetBase):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = (r'^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.select_related('author').prefetch_related(
        'tags',
        'ingredients'
    ).all()
    serializer_class = RecipeSerializer
    permission_classes = (OwnerOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = PageNumberPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        methods=['post', 'delete'],
        detail=True,
    )
    def favorite(self, request, pk):
        created = request.method == 'POST'
        if created:
            obj, status_code = modify_obj(request, pk, Favorite, created)
            return Response(obj, status=status_code)
        obj, status_code = modify_obj(request, pk, Favorite, created)
        return Response(obj, status=status_code)

    @action(
        methods=['post', 'delete'],
        detail=True,
    )
    def shopping_cart(self, request, pk):
        created = request.method == 'POST'
        if created:
            obj, status_code = modify_obj(request, pk, ShoppingCart, created)
            return Response(obj, status=status_code)
        obj, status_code = modify_obj(request, pk, ShoppingCart, created)
        return Response(obj, status=status_code)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        recipe_ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=request.user
        ).select_related('ingredient').order_by('ingredient__name')
        ingredients = [
            ri
            for ri in recipe_ingredients
        ]
        shopping_list = create_shopping_list(ingredients)
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename={0}'.format('shopping_list.txt'))
        return response
