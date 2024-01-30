from rest_framework.permissions import BasePermission, SAFE_METHODS


class AuthorOrReadOnly(BasePermission):
    """Разрешение на уровне автора или только для чтения"""

    def has_object_permission(self, request, view, obj):
        if request.user.is_anonymous:
            return request.method in SAFE_METHODS
        author = (obj.author == request.user,
                  request.user.is_moderator,
                  request.user.is_admin,
                  request.user.is_superuser
                  )
        return (request.method in SAFE_METHODS or any(author))


class IsAuthenticatedOrReadOnly(BasePermission):
    """
    Разрешение на уровне аутентифицированного пользователя
    или только для чтения
    """

    def has_permission(self, request, view):
        return (request.method in SAFE_METHODS
                or request.user.is_authenticated)


class IsAdminOrReadOnly(BasePermission):
    """Разрешение на уровне админа или только для чтения"""

    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return request.method in SAFE_METHODS
        return (request.user.is_admin or request.user.is_superuser)


class IsAdminOrSuperuser(BasePermission):
    """Разрешение на уровне админа/суперюзера или только для чтения"""

    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        return (request.user.is_admin or request.user.is_superuser)
