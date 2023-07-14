from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from recipes.models import Subscription

User = get_user_model()


class CustomUserAdmin(UserAdmin):
    list_filter = ('email', 'username', 'is_staff', 'is_active')
    search_fields = ('username', 'email')


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'subscriber')
    list_filter = ('author', 'subscriber')


register_models = {
    User: CustomUserAdmin,
    Subscription: SubscriptionAdmin,
}

for base_model, admin_model in register_models.items():
    admin.site.register(base_model, admin_model)
