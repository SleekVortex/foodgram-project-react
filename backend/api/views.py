from django.contrib.auth import get_user_model
from recipes.models import (Ingredient,
                            Tag
                            )
from rest_framework import filters, viewsets

from .permissions import ReadOnly
from .serializers import (IngredientSerializer,
                          TagSerializer
                          )

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
