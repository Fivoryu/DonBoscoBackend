from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from django.contrib.auth import authenticate, logout
from rest_framework.authtoken.models import Token
from .models import Usuario, Rol, Notificacion, Bitacora, SuperAdmin, MultiToken, Admin, Puesto, Accion, ModeloPermitido, PermisoPuesto, PermisoRol

from aplicaciones.estudiantes.models import Estudiante, Tutor
from aplicaciones.personal.models import Profesor

from .authentication import MultiTokenAuthentication


from django.contrib.auth.models import User as UserModel
from django.db.models import Count, Q # Importar Count y Q para consultas complejas
from django.views.decorators.csrf import csrf_exempt

import secrets

from .permissions import IsSuperAdmin, PermisoPorRol, PermisoPorPuesto

from .serializer import (

    UsuarioSerializer,
    RolSerializer,
    NotificacionSerializer,
    BitacoraSerializer,
    LoginSerializer,
    SuperAdminSerializer,
    AdminSerializer,
    PuestoSerializer,
    AccionSerializer,
    ModeloPermitidoSerializer,
    PermisoPuestoSerializer,
    PermisoRolSerializer,
)

from django.utils import timezone
from .utils import registrar_bitacora
from django.http import JsonResponse
from django.middleware.csrf import get_token

from .permissions import IsSuperAdmin, IsAdmin

def csrf_token_view(request):
    return JsonResponse({'csrftoken': get_token(request)})

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    authentication_classes = [MultiTokenAuthentication]
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'], permission_classes=[PermisoPorPuesto])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Crear usuario
        user = serializer.save()

        # Asignar rol y crear el objeto correspondiente
        rol_id = request.data.get('rol_id')  # El rol es enviado como un string ('superadmin', 'admin', etc.)
        print(rol_id)
        
        if rol_id:
            try:
                # Obtener el rol correspondiente desde la base de datos
                rol_instance = Rol.objects.get(pk=rol_id)
                user.rol = rol_instance
                user.save()

                nombre = rol_instance.nombre.lower()

                # Crear el objeto correspondiente basado en el rol
                if nombre == 'superadmin':
                    SuperAdmin.objects.create(usuario=user)
                elif nombre == 'admin':
                    Admin.objects.create(usuario=user, puesto=request.data.get('puesto', ''))
                elif nombre == 'profesor':
                    Profesor.objects.create(usuario=user)
                elif nombre == 'estudiante':
                    rude = request.data.get('rude', '').strip()
                    curso_id = request.data.get('curso_id')
                    unidad_id = request.data.get('unidad_id')
                    if not rude:
                        return Response({'error': 'El campo RUDE es obligatorio para estudiantes.'}, status=400)
                    estudiante = Estudiante(
                        usuario=user,
                        rude=rude,
                        curso_id=curso_id,
                        unidad_id=unidad_id
                     )   
                    estudiante.save() 
                elif nombre == 'tutor':
                    Tutor.objects.create(usuario=user, parentesco=request.data.get('parentesco', 'OTR'))
                else:
                    print(f"Rol no reconocido: {rol_instance.nombre}")
                    return Response({'error': 'Rol no válido'}, status=status.HTTP_400_BAD_REQUEST)
            except Rol.DoesNotExist:
                return Response({'error': 'Rol no encontrado'}, status=status.HTTP_400_BAD_REQUEST)

        # Registrar bitácora
        ip = get_client_ip(request)  # Asumiendo que tienes esta función que obtiene la IP
        registrar_bitacora(
            usuario=user,
            ip=ip,
            tabla_afectada='usuario',
            accion='crear',
            descripcion=f'Creación de nuevo usuario: {user.username}'
        )

        return Response({
            'user': serializer.data,
            'message': 'Usuario registrado exitosamente'
        }, status=status.HTTP_201_CREATED)




    @action(
        detail=False,
        methods=['post'],
        permission_classes=[AllowAny],
        url_path='login',
    )
    def login(self, request):
        print("Entrando a login")
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            print("Errores en serializer:", serializer.errors)
            return Response(serializer.errors, status=400)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        print(f"Login attempt: {username=}")

        user = authenticate(username=username, password=password)
        print(f"User auth result: {user}")

        if user is None:
            return Response({'error': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            return Response({'error': 'Cuenta desactivada'}, status=status.HTTP_403_FORBIDDEN)

        token = MultiToken.objects.create(
            user=user,
            key=secrets.token_hex(20),  # 40 caracteres
            device_name=request.headers.get("User-Agent", "")[:250]
        )
        print(token.key)

        # Registrar bitácora si tienes la función
        ip = get_client_ip(request)
        registrar_bitacora(
            usuario=user,
            ip=ip,
            tabla_afectada='usuario',
            accion='crear',
            descripcion='Inicio de sesión exitoso'
        )

        user_data = UsuarioSerializer(user, context={'request': request}).data

        return Response({
            'token': token.key,
            'user': user_data
        })

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        # Registrar bitácora de cierre de sesión
        bitacora = Bitacora.objects.filter(
            usuario=request.user,
            hora_salida__isnull=True
        ).last()

        if bitacora:
            bitacora.hora_salida = timezone.now()
            bitacora.descripcion = "Cierre de sesión"
            bitacora.save()
        else:
            # Opción: registrar nuevo solo si no se encontró uno anterior
            ip = get_client_ip(request)
            Bitacora.objects.create(
                usuario=request.user,
                hora_entrada=timezone.now(),
                hora_salida=timezone.now(),
                ip=ip,
                tabla_afectada="usuario",
                accion="ver",
                descripcion="Cierre de sesión sin entrada previa"
            )

        # Eliminar el token del usuario para terminar la sesión
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Token '):
            token_key = auth_header.split(' ')[1]
            MultiToken.objects.filter(key=token_key).delete()

        # Realizar logout del usuario
        logout(request)

        return Response({'message': 'Sesión cerrada correctamente'})
    
    
    @action(detail=False, methods=['get'], permission_classes=[PermisoPorPuesto],)
    def cantidad(self, request):
        cantidad = Usuario.objects.count()

        return Response({'cantidad_usuarios': cantidad})

    # Cantidad de usuarios por rol
    @action(
        detail=False, 
        methods=['get'],
        url_path='cantidad-por-rol',
        permission_classes=[PermisoPorPuesto]     
    )

    def cantidad_por_rol(self, request):
        """
        Devuelve un diccionario con la cantidad de usuarios por rol.
        """
        qs = Usuario.objects.values('rol__nombre').annotate(cantidad=Count('id'))
        data = {
            item['rol__nombre']: item['cantidad']
            for item in qs
        }

        registrar_bitacora (
            usuario=request.user,
            ip=get_client_ip(request),
            tabla_afectada='usuario',
            accion='ver',
            descripcion='Consultó la cantidad de usuarios por rol'
        )

        return Response(data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='perfil', permission_classes=[IsAuthenticated])
    def perfil(self, request):
        # Aquí request.user siempre es un Usuario autenticado
        print("Entrando a perfil")
        user = request.user
        if not user or not user.is_authenticated:
            return Response({"detail": "No autenticado"}, status=401)
        registrar_bitacora(
            usuario=user,
            ip=get_client_ip(request),
            tabla_afectada='usuario',
            accion='ver',
            descripcion='Consultó su perfil'
        )
        serializer = self.get_serializer(request.user, context={'request': request})
        return Response(serializer.data, status=200)


    @action(
        detail=False,
        methods=['get'],
        url_path='listar-usuarios',
        permission_classes=[PermisoPorPuesto]  # refuerza login en este action
    )
    def listar_usuarios(self, request):
        user = request.user

        # 1) SuperAdmin → todos los usuarios
        if hasattr(user, 'superadmin'):
            qs = Usuario.objects.all()

        # 2) Admin → usuarios de su unidad
        elif hasattr(user, 'admin') and user.admin.unidad:
            unidad = user.admin.unidad
            qs = Usuario.objects.filter(
                Q(admin__unidad=unidad) |
                Q(profesor__unidad=unidad) |
                Q(estudiante__unidad=unidad) |
                Q(
                    tutor__estudiantes__estudiante__unidad=unidad
                ) 
            ).distinct()

        # 3) Cualquier otro rol (Profesor, Estudiante, Tutor, etc.) → NO tiene permiso
        else:
            return Response(
                {'detail': 'No tienes permiso para listar usuarios.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = UsuarioSerializer(qs, many=True)

        # Solo registra bitácora si es un Usuario real y autenticado
        user = request.user
        if isinstance(user, UserModel) and user.is_authenticated:
            registrar_bitacora(
                usuario=user,
                ip=get_client_ip(request),
                tabla_afectada='usuario',
                accion='ver',
                descripcion='Listó los usuarios'
            )

        return Response(serializer.data)
   
    @action(detail=True, methods=['put'], permission_classes=[PermisoPorPuesto], url_path='editar')
    def editar_usuario(self, request, pk=None):
        try:
            usuario = Usuario.objects.get(pk=pk)
        except Usuario.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(usuario, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Guardar cambios normales primero (sin aplicar password)
        usuario = serializer.save()

    # Si se quiere cambiar la contraseña
        nueva_contraseña = request.data.get("password")
        if nueva_contraseña:
            usuario.set_password(nueva_contraseña)
            usuario.save()

        registrar_bitacora(
            usuario=request.user,
            ip=get_client_ip(request),
            tabla_afectada='usuario',
            accion='editar',
            descripcion=f'Editó el usuario con ID {pk}'
        )

        return Response({
            'usuario': serializer.data,
            'message': 'Usuario actualizado exitosamente'
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['delete'], permission_classes=[PermisoPorPuesto], url_path='eliminar')
    def eliminar_usuario(self, request, pk=None):
        try:
            usuario = Usuario.objects.get(pk=pk)
        except Usuario.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    
        usuario.delete()
        registrar_bitacora(
        usuario=request.user,
        ip=get_client_ip(request),
        tabla_afectada='usuario',
        accion='eliminar',
        descripcion=f'Eliminó un usuario  '
    )
    
        return Response({'message': 'Usuario eliminado correctamente'}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='listar-superadmins', permission_classes=[PermisoPorPuesto])
    def listar_superadmins(self, request):
        queryset = SuperAdmin.objects.select_related('usuario').all()
        serializer = SuperAdminSerializer(queryset, many=True)
        
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='listar-admins', permission_classes=[PermisoPorPuesto])
    def listar_admins(self, request):
        """
        Lista todos los administradores registrados en el sistema.
        """
        # Filtrar usuarios que tienen el rol de administrador
        queryset = Usuario.objects.filter(rol__nombre='Admin')  # Ajusta el filtro según tu modelo de roles
        serializer = UsuarioSerializer(queryset, many=True)
        
        # Registrar la acción en la bitácora
        registrar_bitacora(
            usuario=request.user,
            ip=get_client_ip(request),
            tabla_afectada='usuario',
            accion='ver',
            descripcion='Listó los administradores'
        )
        
        return Response(serializer.data)
    

class RolViewSet(viewsets.ModelViewSet):
    queryset = Rol.objects.all()
    serializer_class = RolSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [MultiTokenAuthentication]

    @action(detail=False, methods=['get'], url_path='listar-roles')
    def listar_roles(self, request):
        """
        GET /user/auth/roles/listar-roles/
        """
        print(IsSuperAdmin)
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)
    
    @csrf_exempt
    @action(detail=False, methods=['post'], url_path='crear-rol')
    def crear_rol(self, request):
        """
        POST /user/auth/roles/crear-rol/
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rol = serializer.save()
        return Response(self.get_serializer(rol).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['put'], url_path='editar-rol')
    def editar_rol(self, request, pk=None):
        """
        PUT /user/auth/roles/editar-rol/{id}/
        """
        rol = self.get_object()
        serializer = self.get_serializer(rol, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        rol = serializer.save()
        return Response(self.get_serializer(rol).data)

    @action(detail=True, methods=['delete'], url_path='eliminar-rol')
    def eliminar_rol(self, request, pk=None):
        """
        DELETE /user/auth/roles/eliminar-rol/{id}/
        """
        rol = self.get_object()
        rol.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class NotificacionViewSet(viewsets.ModelViewSet):
    serializer_class = NotificacionSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [MultiTokenAuthentication]

    def get_queryset(self):
        return Notificacion.objects.filter(usuario=self.request.user)

    @action(detail=True, methods=['post'])
    def marcar_leida(self, request, pk=None):
        notificacion = self.get_object()
        notificacion.leida = True
        notificacion.save()
        return Response({'status': 'notificación marcada como leída'})
    

from rest_framework.pagination import PageNumberPagination

class BitacoraPagination(PageNumberPagination):
    page_size = 30
    page_query_param = 'page'
    page_size_query_param = 'page_size'
    max_page_size = 100


class BitacoraViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BitacoraSerializer
    permission_classes = [PermisoPorPuesto]
    authentication_classes = [MultiTokenAuthentication]
    pagination_class = BitacoraPagination

    def get_queryset(self):
        qs = Bitacora.objects.all().order_by('-hora_entrada')
        usuario_id = self.request.query_params.get('usuario')
        if usuario_id:
            qs = qs.filter(usuario__id=usuario_id)
        return qs

    @action(detail=False, methods=['get'], url_path='listar')
    def listar(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
class PuestoViewSet(viewsets.ModelViewSet):
    queryset = Puesto.objects.all()
    serializer_class = PuestoSerializer
    permission_classes = [PermisoPorPuesto]
    authentication_classes = [MultiTokenAuthentication]

    @action(detail=False, methods=['get'], url_path='listar-puestos')
    def listar_puestos(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='crear-puesto')
    def crear_puesto(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            puesto = serializer.save()
            return Response(self.get_serializer(puesto).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['put'], url_path='editar-puesto')
    def editar_puesto(self, request, pk=None):
        try:
            puesto = Puesto.objects.get(pk=pk)
        except Puesto.DoesNotExist:
            return Response({'error': 'Puesto no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(puesto, data=request.data, partial=True)
        if serializer.is_valid():
            puesto = serializer.save()
            return Response(self.get_serializer(puesto).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'], url_path='eliminar-puesto')
    def eliminar_puesto(self, request, pk=None):
        try:
            puesto = Puesto.objects.get(pk=pk)
        except Puesto.DoesNotExist:
            return Response({'error': 'Puesto no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        puesto.delete()
        return Response({'message': 'Puesto eliminado correctamente'}, status=status.HTTP_204_NO_CONTENT)

class AdminViewSet(viewsets.ModelViewSet):
    queryset = Admin.objects.select_related('usuario', 'puesto', 'unidad').all()
    serializer_class = AdminSerializer
    permission_classes = [PermisoPorPuesto]
    authentication_classes = [MultiTokenAuthentication]

    @action(detail=False, methods=['get'], url_path='listar-admins')
    def listar_admins(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='crear-admin')
    def crear_admin(self, request):
        """
        Crea un Admin. Si usuario_id está presente, usa ese usuario.
        Si no, crea un nuevo usuario con los datos enviados.
        Espera: usuario_id (opcional), datos de usuario (si no existe), puesto_id, unidad, estado
        """
        usuario_id = request.data.get('usuario_id')
        if usuario_id:
            # Usar usuario existente
            try:
                usuario = Usuario.objects.get(pk=usuario_id)
            except Usuario.DoesNotExist:
                return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Crear nuevo usuario
            # Extraer campos de usuario directamente de request.data
            usuario_fields = [
                'ci', 'foto', 'nombre', 'apellido', 'sexo', 'email',
                'fecha_nacimiento', 'username', 'estado', 'password', 'rol_id'
            ]
            usuario_data = {k: request.data.get(k) for k in usuario_fields if k in request.data}
            if not usuario_data.get('ci') or not usuario_data.get('nombre') or not usuario_data.get('apellido'):
                return Response({'error': 'Datos de usuario requeridos'}, status=status.HTTP_400_BAD_REQUEST)
            usuario_serializer = UsuarioSerializer(data=usuario_data)
            if not usuario_serializer.is_valid():
                return Response(usuario_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            usuario = usuario_serializer.save()
            # Asignar rol admin si no viene en el payload
            if not usuario_data.get('rol_id'):
                try:
                    rol_admin = Rol.objects.get(nombre__iexact='admin')
                    usuario.rol = rol_admin
                    usuario.save()
                except Rol.DoesNotExist:
                    return Response({'error': 'Rol admin no encontrado'}, status=status.HTTP_400_BAD_REQUEST)

        # Crear el admin
        admin_data = request.data.copy()
        admin_data['usuario_id'] = usuario.pk
        # Asegura que los campos sean id, no objetos ni strings vacíos
        if 'puesto_id' in admin_data and not admin_data['puesto_id']:
            admin_data['puesto_id'] = None
        if 'unidad_id' in admin_data and not admin_data['unidad_id']:
            admin_data['unidad_id'] = None
        serializer = self.get_serializer(data=admin_data)
        if serializer.is_valid():
            admin = serializer.save()
            return Response(self.get_serializer(admin).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['put'], url_path='editar-admin')
    def editar_admin(self, request, pk=None):
        try:
            admin = Admin.objects.get(pk=pk)
        except Admin.DoesNotExist:
            return Response({'error': 'Admin no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(admin, data=request.data, partial=True)
        if serializer.is_valid():
            admin = serializer.save()
            return Response(self.get_serializer(admin).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'], url_path='eliminar-admin')
    def eliminar_admin(self, request, pk=None):
        try:
            admin = Admin.objects.get(pk=pk)
        except Admin.DoesNotExist:
            return Response({'error': 'Admin no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        admin.delete()
        return Response({'message': 'Admin eliminado correctamente'}, status=status.HTTP_204_NO_CONTENT)

class AccionViewSet(viewsets.ModelViewSet):
    queryset = Accion.objects.all()
    serializer_class = AccionSerializer
    permission_classes = [PermisoPorPuesto]
    authentication_classes = [MultiTokenAuthentication]

class ModeloPermitidoViewSet(viewsets.ModelViewSet):
    queryset = ModeloPermitido.objects.all()
    serializer_class = ModeloPermitidoSerializer
    permission_classes = [PermisoPorPuesto]
    authentication_classes = [MultiTokenAuthentication]

class PermisoPuestoViewSet(viewsets.ModelViewSet):
    queryset = PermisoPuesto.objects.select_related('puesto', 'modelo', 'accion').all()
    serializer_class = PermisoPuestoSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [MultiTokenAuthentication]

    def get_queryset(self):
        queryset = super().get_queryset()
        puesto_id = self.request.query_params.get('puesto_id')
        if puesto_id:
            try:
                puesto_id_int = int(puesto_id)
                queryset = queryset.filter(puesto__id=puesto_id_int)
            except ValueError:
                queryset = queryset.none()
        return queryset

    def list(self, request, *args, **kwargs):
        puesto_id = request.query_params.get('puesto_id')
        if not puesto_id:
            return Response([], status=200)
        queryset = self.get_queryset()
        print(f"[DEBUG] PermisoPuestoViewSet.list puesto_id={puesto_id} count={queryset.count()}")
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
class PermisoRolViewSet(viewsets.ModelViewSet):
    """
    CRUD de permisos por Rol. Solo Admin/SuperAdmin pueden modificar.
    """
    queryset = PermisoRol.objects.select_related('rol', 'modelo', 'accion')
    serializer_class = PermisoRolSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [MultiTokenAuthentication]

def get_client_ip(request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip
