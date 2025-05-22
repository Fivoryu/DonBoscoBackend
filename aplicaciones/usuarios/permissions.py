from rest_framework.permissions import BasePermission

class IsSuperAdmin(BasePermission):
    """
    Permite el acceso solo a usuarios que estén relacionados con el modelo SuperAdmin.
    """
    def has_permission(self, request, view):
        return hasattr(request.user, 'superadmin') and request.user.is_authenticated

class IsAdmin(BasePermission):
    """
    Permite el acceso solo a usuarios que estén relacionados con el modelo Admin.
    """
    def has_permission(self, request, view):
        return hasattr(request.user, 'admin') and request.user.is_authenticated
    
class IsAdminOrSuperAdmin(BasePermission):
    """
    Permite el acceso solo a usuarios que sean Admin o SuperAdmin.
    """
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return hasattr(user, 'admin') or hasattr(user, 'superadmin')