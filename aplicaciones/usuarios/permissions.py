from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import PermisoPuesto, PermisoRol, Accion, ModeloPermitido


_METHOD_TO_ACTION = {
    'GET':    'view',
    'HEAD':   'view',
    'OPTIONS':'view',
    'POST':   'add',
    'PUT':    'change',
    'PATCH':  'change',
    'DELETE': 'delete',
}

def metodo_a_accion(method: str) -> str:
    """
    Mapea el método HTTP a la acción correspondiente.
    """
    return _METHOD_TO_ACTION.get(method, Accion.nombre)

# ──────────────────────────────────────────────────────────────
#  Permisos base por tipo de usuario
# ──────────────────────────────────────────────────────────────
class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'superadmin')


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'admin')


class IsAdminOrSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        u = request.user
        return u.is_authenticated and (hasattr(u, 'admin') or hasattr(u, 'superadmin'))


class IsEstudiante(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'estudiante')


class IsProfesor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'profesor')


class IsTutor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'tutor')


class IsProfesorOrTutor(BasePermission):
    def has_permission(self, request, view):
        u = request.user
        return u.is_authenticated and (hasattr(u, 'profesor') or hasattr(u, 'tutor'))


    
# ──────────────────────────────────────────────────────────────
#  PermisoPorPuesto → Admin con cargos variables
# ──────────────────────────────────────────────────────────────
class PermisoPorPuesto(BasePermission):
    """
    Consulta la tabla PermisoPuesto:
    (puesto, modelo, accion)
    """
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False

        # SuperAdmin bypass
        if hasattr(user, 'superadmin'):
            return True

        # Solo Admin usa este permiso
        if not hasattr(user, 'admin'):
            # Otros roles pasan a PermisoPorRol o a lógica específica
            return request.method in SAFE_METHODS

        admin   = user.admin
        puesto  = admin.puesto
        modelo  = view.basename
        accion  = metodo_a_accion(request.method)

        return PermisoPuesto.objects.filter(
            puesto=puesto,
            modelo__nombre=modelo,
            accion__nombre=accion
        ).exists()
    
# ──────────────────────────────────────────────────────────────
#  PermisoPorRol → roles fijos (Estudiante, Profesor, Tutor…)
# ──────────────────────────────────────────────────────────────
class PermisoPorRol(BasePermission):
    """
    Usa (rol, modelo, accion) de la tabla PermisoRol.
    Pasa si existe al menos una fila que coincida.
    """

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False

        # SuperAdmin bypass
        if hasattr(user, 'superadmin'):
            return True

        # Admin se delega a PermisoPorPuesto
        if hasattr(user, 'admin'):
            return True   # lo evaluará PermisoPorPuesto en la lista de permisos

        # Resto de usuarios deben tener un Rol
        if not user.rol_id:
            return request.method in SAFE_METHODS

        accion = metodo_a_accion(request.method)
        modelo = view.basename

        return PermisoRol.objects.filter(
            rol_id=user.rol_id,
            modelo__nombre=modelo,
            accion__nombre=accion
        ).exists()
    

# ──────────────────────────────────────────────────────────────
#  PermisoEstudianteView → regla específica de negocio
# ──────────────────────────────────────────────────────────────
class PermisoEstudianteView(BasePermission):
    """
    Combina:
      • SuperAdmin → todo
      • Admin      → PermisoPorPuesto
      • Otros roles → PermisoPorRol
      • Tutor      → lectura solo si está vinculado al estudiante
      • Profesor   → lectura si tutor del curso O dicta materia en ese curso
      • Estudiante → solo su propio registro
    """

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False

        # SuperAdmin bypass
        if hasattr(user, 'superadmin'):
            return True

        # Admin → validamos con PermisoPorPuesto
        if hasattr(user, 'admin'):
            return PermisoPorPuesto().has_permission(request, view)

        # Otros roles → validamos con PermisoPorRol
        return PermisoPorRol().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        user = request.user

        # SuperAdmin / Admin ya pasaron
        if hasattr(user, 'superadmin') or hasattr(user, 'admin'):
            return True

        # Estudiante: solo suya
        if hasattr(user, 'estudiante'):
            return obj.pk == user.pk

        # Tutor: vínculo en TutorEstudiante
        if hasattr(user, 'tutor'):
            return obj.tutores.filter(tutor__usuario=user).exists()

        # Profesor: tutor del curso o dicta alguna materia en ese curso
        if hasattr(user, 'profesor'):
            prof  = user.profesor
            curso = obj.curso
            if not curso:
                return False

            # 1) Tutor del curso
            if curso.tutor_id == prof.pk:
                return True

            # 2) Profesor asignado en MateriaCurso
            from aplicaciones.academico.models import MateriaCurso
            return MateriaCurso.objects.filter(curso=curso, profesor=prof).exists()

        # Cualquier otro rol (visitante) → denegado
        return False