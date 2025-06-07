from rest_framework.permissions import BasePermission
from .models import PermisoPuesto

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
    
class IsEstudiante(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'estudiante') and request.user.is_authenticated

class IsProfesor(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'profesor') and request.user.is_authenticated

class IsTutor(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'tutor') and request.user.is_authenticated
    
class IsProfesorOrTutor(BasePermission):
    def has_permission(self, request, view):
        return (
            (hasattr(request.user, 'profesor') or hasattr(request.user, 'tutor'))
            and request.user.is_authenticated
        )
    
class PermisoPorPuesto(BasePermission):
    """
    Revisa si el admin con cierto puesto puede hacer la acción sobre el modelo.
    """
    def has_permission(self, request, view):
        # Permitir acceso a superadmin SIEMPRE
        if hasattr(request.user, 'superadmin'):
            return True

        # Permitir acceso a todos los usuarios autenticados para endpoints públicos o de solo lectura
        # Por ejemplo, para endpoints de conteo o dashboard, puedes permitir GET aunque no haya puesto
        if request.method == 'GET' and not hasattr(request.user, 'admin'):
            return True

        if hasattr(request.user, 'admin'):
            admin = request.user.admin
            puesto = admin.puesto
            modelo = view.basename  # nombre del modelo del ViewSet, ej: 'profesor'
            accion = self.metodo_a_accion(request.method)
            # Consulta en PermisoPuesto
            return PermisoPuesto.objects.filter(
                puesto=puesto,
                modelo__nombre=modelo,
                accion__nombre=accion
            ).exists()
        return False

    def metodo_a_accion(self, method):
        # Mapea el método HTTP a acción
        return {
            'GET': 'view',
            'POST': 'add',
            'PUT': 'change',
            'PATCH': 'change',
            'DELETE': 'delete'
        }.get(method, 'view')