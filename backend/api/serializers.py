import base64
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import InMemoryUploadedFile
from djoser.serializers import UserSerializer as DjoserUserSerializer
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Subscription, Tag)
from rest_framework import serializers

User = get_user_model()


class UserSerializer(DjoserUserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        current_user = None
        if self.context.get('request'):
            current_user = self.context['request'].user
        if current_user and current_user.is_authenticated:
            return Subscription.objects.filter(
                author=obj, subscriber=current_user).exists()
        return False

    class Meta:
        model = User
        fields = ('email', 'id',
                  'username', 'first_name',
                  'last_name', 'is_subscribed',
                  )


class SubscriptionSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    def get_recipes(self, obj):
        request = self.context.get('request')
        number_recipes = int(request.GET.get('recipes_limit', 0))
        recipes = Recipe.objects.filter(author=obj)
        if number_recipes:
            recipes = recipes[:number_recipes]
        return RecipeListSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def validate(self, data):
        if self.context['request'].user == data.get('author'):
            raise serializers.ValidationError(
                "Нельзя подписаться на самого себя.")
        return data

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count',)


class RecipeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)
        read_only_fields = ('name', 'text',
                            'author', 'image',
                            'cooking_time', 'tags',
                            'created',
                            )


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class ImageSerializer(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            name = self.context["request"].user.username
            decoded_image = base64.b64decode(imgstr)
            file = BytesIO(decoded_image)
            data = InMemoryUploadedFile(
                file,
                field_name='image',
                name=f'{name}.' + ext,
                content_type='image/' + ext,
                size=len(decoded_image),
                charset=None
            )
        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class RecipeSerializer(serializers.ModelSerializer):
    is_in_shopping_cart = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientSerializer(
        source='recipeingredient_set',
        many=True,
        read_only=True,
    )
    image = ImageSerializer(use_url=True)

    def __create_recipe_ingredient_objects(self, recipe, ingredients):
        obj = (RecipeIngredient(
            recipe=recipe, ingredient_id=ing['id'], amount=ing['amount']
        ) for ing in ingredients)
        RecipeIngredient.objects.bulk_create(obj)

    def get_is_in_shopping_cart(self, obj):
        current_user = self.context['request'].user
        if current_user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            recipe=obj, user=current_user).exists()

    def get_is_favorited(self, obj):
        current_user = self.context['request'].user
        if current_user.is_anonymous:
            return False
        return Favorite.objects.filter(
            recipe=obj, user=current_user).exists()

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        RecipeIngredient.objects.filter(recipe=instance).all().delete()
        self.__create_recipe_ingredient_objects(instance, ingredients)
        tags = validated_data.pop('tags', None)
        if tags:
            instance.tags.set(tags)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        return super().update(instance, validated_data)

    def validate_ingredients(self, value):
        ingredients = value
        ingredients_ids = set()
        for ingredient in ingredients:
            if not ingredient.get('amount') or not ingredient.get('id'):
                raise serializers.ValidationError(
                    'Убедитесь, что поле `ингредиенты` заполнено верно.')
            if not int(ingredient['amount']) > 0:
                raise serializers.ValidationError(
                    'Количество ингредиента должно быть больше нуля.')
            if ingredient['id'] in ingredients_ids:
                raise serializers.ValidationError(
                    'Ингредиенты не должны повторяться.')
            ingredients_ids.add(ingredient['id'])
        return value

    def validate_tags(self, value):
        tags = value
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(
                'Теги не должны повторяться.')
        return value

    def validate_name(self, name):
        if not any(c.isalpha() for c in name):
            raise serializers.ValidationError(
                'В названии рецепта должна быть хотя бы одна буква.')
        return name

    def create(self, validated_data):
        tags = self.initial_data.get('tags')
        ingredients = self.initial_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.__create_recipe_ingredient_objects(recipe, ingredients)
        return recipe

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')
