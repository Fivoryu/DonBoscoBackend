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
    def has_permission(self, request, view):
        print(f"[PermisoPorPuesto] Evaluando permiso para: {request.user}")
        print(f"[PermisoPorPuesto] Método: {request.method}, View: {view.basename}")

        # Superadmin siempre tiene acceso
        if hasattr(request.user, 'superadmin'):
            print("[PermisoPorPuesto] Usuario es SuperAdmin: acceso concedido.")
            return True

        # Permitir GET si no es admin (ej: público autenticado viendo dashboard)
        if request.method == 'GET' and not hasattr(request.user, 'admin'):
            print("[PermisoPorPuesto] Usuario no es admin pero está autenticado con GET: acceso concedido.")
            return True

        if hasattr(request.user, 'admin'):
            admin = request.user.admin
            puesto = admin.puesto
            modelo = view.basename
            accion = self.metodo_a_accion(request.method)

            print(f"[PermisoPorPuesto] Admin: {admin}, Puesto: {puesto}, Modelo: {modelo}, Acción: {accion}")

            permiso_existe = PermisoPuesto.objects.filter(
                puesto=puesto,
                modelo__nombre=modelo,
                accion__nombre=accion
            ).exists()

            print(f"[PermisoPorPuesto] ¿Permiso encontrado en la BD? {permiso_existe}")
            return permiso_existe

        print("[PermisoPorPuesto] Usuario no tiene relación con Admin ni SuperAdmin: acceso denegado.")
        return False

    def metodo_a_accion(self, method):
        return {
            'GET': 'view',
            'POST': 'add',
            'PUT': 'change',
            'PATCH': 'change',
            'DELETE': 'delete'
        }.get(method, 'view')
