from rest_framework.permissions import BasePermission, SAFE_METHODS


class ReadOnly(BasePermission):
    message = 'Метод запрещен'

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class OwnerOrReadOnly(BasePermission):
    message = 'Метод запрещен, так как вы не владелец контента'

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.user == obj.author
            or request.method in SAFE_METHODS
        )
