from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.views.decorators.csrf import csrf_exempt
from aplicaciones.usuarios.permissions import IsAdminOrSuperAdmin
from aplicaciones.usuarios.utils import registrar_bitacora
from aplicaciones.usuarios.authentication import MultiTokenAuthentication
from aplicaciones.usuarios.usuario_views import get_client_ip

from .models import Especialidad, Profesor, ProfesorEspecialidad
from .serializers import (
    EspecialidadSerializer, CreateEspecialidadSerializer,
    ProfesorSerializer,    CreateProfesorSerializer,
    ProfesorEspecialidadSerializer, CreateProfesorEspecialidadSerializer,
    UpdateProfesorSerializer

)


class EspecialidadViewSet(viewsets.ModelViewSet):
    queryset = Especialidad.objects.all()
    permission_classes = [IsAdminOrSuperAdmin]
    authentication_classes = [MultiTokenAuthentication]

    def get_serializer_class(self):
        if self.action in ['crear', 'editar']:
            return CreateEspecialidadSerializer
        return EspecialidadSerializer

    @action(detail=False, methods=['get'], url_path='listar')
    def listar(self, request):
        qs = self.get_queryset()
        serializer = EspecialidadSerializer(qs, many=True)
        registrar_bitacora(request.user, get_client_ip(request),
                           'especialidad', 'ver', 'Listó especialidades')
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='crear')
    @csrf_exempt
    def crear(self, request):
        serializer = CreateEspecialidadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        esp = serializer.save()
        registrar_bitacora(request.user, get_client_ip(request),
                           'especialidad', 'crear', f'Creó {esp}')
        return Response(EspecialidadSerializer(esp).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['put'], url_path='editar')
    def editar(self, request, pk=None):
        try:
            esp = Especialidad.objects.get(pk=pk)
        except Especialidad.DoesNotExist:
            return Response({'detail':'No encontrado'}, status=status.HTTP_404_NOT_FOUND)
        serializer = CreateEspecialidadSerializer(esp, data=request.data)
        serializer.is_valid(raise_exception=True)
        esp = serializer.save()
        registrar_bitacora(request.user, get_client_ip(request),
                           'especialidad', 'editar', f'Editó {esp}')
        return Response(EspecialidadSerializer(esp).data)

    @action(detail=True, methods=['delete'], url_path='eliminar')
    def eliminar(self, request, pk=None):
        try:
            esp = Especialidad.objects.get(pk=pk)
        except Especialidad.DoesNotExist:
            return Response({'detail':'No encontrado'}, status=status.HTTP_404_NOT_FOUND)
        esp.delete()
        registrar_bitacora(request.user, get_client_ip(request),
                           'especialidad', 'eliminar', f'Eliminó especialidad {pk}')
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProfesorViewSet(viewsets.ModelViewSet):
    queryset = Profesor.objects.all()
    permission_classes = [IsAdminOrSuperAdmin]
    authentication_classes = [MultiTokenAuthentication]

    def get_serializer_class(self):
        if self.action in ['create', 'crear']:
            return CreateProfesorSerializer
        if self.action == 'editar':
            return UpdateProfesorSerializer
        return ProfesorSerializer

    @action(detail=False, methods=['get'], url_path='listar')
    def listar(self, request):
        qs = self.get_queryset()
        serializer = ProfesorSerializer(qs, many=True)
        registrar_bitacora(request.user, get_client_ip(request),
                           'profesor', 'ver', 'Listó profesores')
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='crear')
    @csrf_exempt
    def crear(self, request):
        serializer = CreateProfesorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        prof = serializer.save()
        registrar_bitacora(request.user, get_client_ip(request),
                           'profesor', 'crear', f'Creó {prof}')
        return Response(ProfesorSerializer(prof).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['put'], url_path='editar')
    def editar(self, request, pk=None):
        print("Entrando a editar")
        prof = self.get_object()
        serializer = self.get_serializer(prof, data=request.data)
        serializer.is_valid(raise_exception=True)
        prof = serializer.save()

        registrar_bitacora(request.user, get_client_ip(request),
                           'profesor', 'editar', f'Editó {prof}')
        return Response(ProfesorSerializer(prof).data)

    @action(detail=True, methods=['delete'], url_path='eliminar')
    def eliminar(self, request, pk=None):
        try:
            prof = Profesor.objects.get(pk=pk)
        except Profesor.DoesNotExist:
            return Response({'detail':'No encontrado'}, status=status.HTTP_404_NOT_FOUND)
        prof.delete()
        registrar_bitacora(request.user, get_client_ip(request),
                           'profesor', 'eliminar', f'Eliminó profesor {pk}')
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProfesorEspecialidadViewSet(viewsets.ModelViewSet):
    queryset = ProfesorEspecialidad.objects.select_related('profesor', 'especialidad')
    permission_classes = [IsAdminOrSuperAdmin]
    authentication_classes = [MultiTokenAuthentication]

    def get_serializer_class(self):
        if self.action in ['crear', 'editar']:
            return CreateProfesorEspecialidadSerializer
        return ProfesorEspecialidadSerializer

    @action(detail=False, methods=['get'], url_path='listar')
    def listar(self, request):
        qs = self.get_queryset()
        serializer = ProfesorEspecialidadSerializer(qs, many=True)
        registrar_bitacora(request.user, get_client_ip(request),
                           'profesor_especialidad', 'ver', 'Listó asignaciones')
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='crear')
    @csrf_exempt
    def crear(self, request):
        serializer = CreateProfesorEspecialidadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pe = serializer.save()
        registrar_bitacora(request.user, get_client_ip(request),
                           'profesor_especialidad', 'crear', f'Asignó {pe}')
        return Response(ProfesorEspecialidadSerializer(pe).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['put'], url_path='editar')
    def editar(self, request, pk=None):
        try:
            pe = ProfesorEspecialidad.objects.get(pk=pk)
        except ProfesorEspecialidad.DoesNotExist:
            return Response({'detail':'No encontrado'}, status=status.HTTP_404_NOT_FOUND)
        serializer = CreateProfesorEspecialidadSerializer(pe, data=request.data)
        serializer.is_valid(raise_exception=True)
        pe = serializer.save()
        registrar_bitacora(request.user, get_client_ip(request),
                           'profesor_especialidad', 'editar', f'Editó {pe}')
        return Response(ProfesorEspecialidadSerializer(pe).data)

    @action(detail=True, methods=['delete'], url_path='eliminar')
    def eliminar(self, request, pk=None):
        try:
            pe = ProfesorEspecialidad.objects.get(pk=pk)
        except ProfesorEspecialidad.DoesNotExist:
            return Response({'detail':'No encontrado'}, status=status.HTTP_404_NOT_FOUND)
        pe.delete()
        registrar_bitacora(request.user, get_client_ip(request),
                           'profesor_especialidad', 'eliminar', f'Removió {pe}')
        return Response(status=status.HTTP_204_NO_CONTENT)
