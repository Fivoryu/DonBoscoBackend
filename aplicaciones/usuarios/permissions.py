from rest_framework.permissions import BasePermission

class IsSuperAdmin(BasePermission):
    """
    Permite el acceso solo a usuarios que estén relacionados con el modelo SuperAdmin.
    """
    def has_permission(self, request, view):
        return hasattr(request.user, 'superadmin') and request.user.is_authenticated
