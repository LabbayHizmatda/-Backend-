from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    """
    Разрешение для проверки, является ли пользователь администратором.
    """

    def has_permission(self, request, view):
        if 'Admin' in request.user.roles:
            return True
        return False
    

