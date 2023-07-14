from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import (Favorite,
                            Ingredient,
                            Recipe,
                            RecipeIngredient,
                            ShoppingCart,
                            Tag,
                            Subscription
                            )
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import RecipeFilter
from .permissions import OwnerOrReadOnly, ReadOnly
from .serializers import (IngredientSerializer,
                          RecipeSerializer,
                          SubscriptionSerializer,
                          TagSerializer,
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

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class UserViewSet(UserViewSet):
    serializer_class = SubscriptionSerializer
    pagination_class = PageNumberPagination
    http_method_names = ['get', 'post']

    @action(methods=['get'], detail=False,
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        authors = User.objects.filter(subscription__subscriber=request.user)
        page = self.paginate_queryset(authors)
        if page is not None:
            serializer = self.get_serializer(
                page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(
            authors, many=True, context={'request': request})
        return Response(serializer.data)

    @action(methods=['post'], detail=True,
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id):
        author = get_object_or_404(User, pk=id)
        if request.user == author:
            return Response(
                {"errors": "Нельзя подписаться на самого себя."},
                status=status.HTTP_400_BAD_REQUEST)
        _, created = Subscription.objects.get_or_create(
            author=author, subscriber=request.user)
        if not created:
            return Response(
                {"errors": "Вы уже подписаны на этого автора."},
                status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(
            author, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id):
        author = get_object_or_404(
            User,
            pk=id,
        )
        subscription = get_object_or_404(
            Subscription,
            author=author,
            subscriber=request.user,
        )
        subscription.delete()
        return Response({"success": "Вы успешно отписаны."},
                        status=status.HTTP_204_NO_CONTENT)
