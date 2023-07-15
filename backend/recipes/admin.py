from django.contrib import admin

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    min_num = 1
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'added_to_favorites')
    list_filter = ('tags', 'name', 'author')
    search_fields = ('name', 'author__username', 'tags__slug', 'tags__name')
    filter_horizontal = ('tags',)
    inlines = (RecipeIngredientInline,)

    @staticmethod
    def added_to_favorites(self, obj):
        return obj.favorites.count()

    added_to_favorites.short_description = 'Добавления в избранное'


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    list_editable = ('color', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_editable = ('measurement_unit',)
    list_filter = ('name',)
    search_fields = ('name',)


class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount')
    list_editable = ('amount',)


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe_list_display')

    def recipe_list_display(self, obj):
        return ', '.join([recipe.name for recipe in obj.recipe.all()])

    recipe_list_display.short_description = 'Recipes'


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'user')


register_models = {
    Recipe: RecipeAdmin,
    Tag: TagAdmin,
    Ingredient: IngredientAdmin,
    RecipeIngredient: RecipeIngredientAdmin,
    Favorite: FavoriteAdmin,
    ShoppingCart: ShoppingCartAdmin,
}

for base_model, admin_model in register_models.items():
    admin.site.register(base_model, admin_model)
