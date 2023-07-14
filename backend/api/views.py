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
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly
                                        )
from rest_framework.response import Response

from .filters import RecipeFilter
from .permissions import OwnerOrReadOnly, ReadOnly
from .serializers import (IngredientSerializer,
                          RecipeSerializer,
                          SubscriptionSerializer,
                          TagSerializer,
                          )
from .utils import create_shopping_list

User = get_user_model()


class ReadOnlyViewSetBase(viewsets.ReadOnlyModelViewSet):
    permission_classes = (ReadOnly,)
    pagination_class = None
    http_method_names = ['get']


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
    permission_classes = (IsAuthenticatedOrReadOnly,
                          OwnerOrReadOnly)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = PageNumberPagination

    @action(methods=['post', 'delete'], detail=True)
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        favorite, created = Favorite.objects.get_or_create(
            user=request.user,
            recipe=recipe
        )
        if not created:
            favorite.delete()
        serializer = RecipeSerializer(recipe)
        return Response(serializer.data)

    @action(methods=['post', 'delete'], detail=True)
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        cart, created = ShoppingCart.objects.get_or_create(
            user=request.user,
            recipe=recipe
        )
        if not created:
            cart.delete()
        serializer = RecipeSerializer(recipe)
        return Response(serializer.data)

    @action(methods=['get'], detail=False)
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__in=ShoppingCart.objects.filter(
                user=request.user).values_list('recipe')
        )
        shopping_list = create_shopping_list(ingredients)
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        return response

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class UserViewSet(UserViewSet):
    serializer_class = SubscriptionSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAuthenticated,)
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
