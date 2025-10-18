from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Разрешает редактировать/удалять только автору или админу."""

    def has_permission(self, request, view):
        # Создавать можно только авторизованным
        if view.action == "create":
            return request.user and request.user.is_authenticated
        return True

    def has_object_permission(self, request, view, obj):
        # Просмотр (GET, HEAD, OPTIONS) — доступен всем
        if request.method in permissions.SAFE_METHODS:
            return True
        # Остальное — только автору или администратору
        return obj.creator == request.user or request.user.is_staff
