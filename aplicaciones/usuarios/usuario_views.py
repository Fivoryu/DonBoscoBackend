from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from django.contrib.auth import authenticate, logout
from rest_framework.authtoken.models import Token
from .models import Usuario, Rol, Notificacion, Bitacora, SuperAdmin, MultiToken

from .authentication import MultiTokenAuthentication


from django.contrib.auth.models import User as UserModel
from django.db.models import Count # Importar Count para contar usuarios
from django.views.decorators.csrf import csrf_exempt

import secrets

from .serializer import (

    UsuarioSerializer,
    RolSerializer,
    NotificacionSerializer,
    BitacoraSerializer,
    LoginSerializer,
    SuperAdminSerializer,
)

from django.utils import timezone
from .utils import registrar_bitacora

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    authentication_classes = [MultiTokenAuthentication]
    permission_classes = [IsAuthenticated]

    def register(self, request):
        print("inteto de registro")
        serializer = self.get_serializer(data=request.data)
        print("Datos iniciales enviados al serializador:", serializer.initial_data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user = serializer.save()
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

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
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
    
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny],)
    def cantidad(self, request):
        cantidad = Usuario.objects.count()

        return Response({'cantidad_usuarios': cantidad})

    # Cantidad de usuarios por rol
    @action(
        detail=False, 
        methods=['get'],
        url_path='cantidad-por-rol',
        permission_classes=[IsAuthenticated]     
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
    
    @action(detail=False, methods=['get'], url_path='perfil')
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
        permission_classes=[IsAuthenticated]  # refuerza login en este action
    )
    def listar_usuarios(self, request):
        usuarios = Usuario.objects.all()
        serializer = UsuarioSerializer(usuarios, many=True)

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
   
    @action(detail=True, methods=['put'], permission_classes=[permissions.IsAdminUser])
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

    @action(detail=True, methods=['delete'], permission_classes=[permissions.IsAdminUser])
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

    @action(detail=False, methods=['get'], url_path='listar-superadmins', permission_classes=[permissions.IsAdminUser])
    def listar_superadmins(self, request):
        queryset = SuperAdmin.objects.select_related('usuario').all()
        serializer = SuperAdminSerializer(queryset, many=True)
        
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='listar-admins', permission_classes=[permissions.IsAdminUser])
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
    permission_classes = [permissions.IsAdminUser]

class NotificacionViewSet(viewsets.ModelViewSet):
    serializer_class = NotificacionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notificacion.objects.filter(usuario=self.request.user)

    @action(detail=True, methods=['post'])
    def marcar_leida(self, request, pk=None):
        notificacion = self.get_object()
        notificacion.leida = True
        notificacion.save()
        return Response({'status': 'notificación marcada como leída'})

class BitacoraViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BitacoraSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return Bitacora.objects.all().order_by('-hora_entrada')


def get_client_ip(request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip
