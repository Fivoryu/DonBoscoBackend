from argparse import Action
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from aplicaciones.usuarios import permissions
from .serializers import UpdateEstadoLicenciaSerializer 
from aplicaciones.usuarios.authentication import MultiTokenAuthentication
from rest_framework import status

from .models import (
    Comportamiento,
    Licencia,
    AsistenciaGeneral,
    AsistenciaClase
)
from .serializers import (
    ComportamientoSerializer,
    LicenciaSerializer,
    AsistenciaGeneralSerializer,
    AsistenciaClaseSerializer,
    CreateComportamientoSerializer,
    CreateLicenciaSerializer,
    CreateAsistenciaGeneralSerializer,
    CreateAsistenciaClaseSerializer
)

class ComportamientoViewSet(viewsets.ModelViewSet):
    queryset = Comportamiento.objects.all()
    filterset_fields = ['estudiante', 'tipo', 'fecha']
    search_fields = ['descripcion']
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CreateComportamientoSerializer
        return ComportamientoSerializer

class LicenciaViewSet(viewsets.ModelViewSet):
    queryset = Licencia.objects.select_related('estudiante__usuario', 'tutor__usuario').all()
    authentication_classes = [MultiTokenAuthentication]
    permission_classes = [permissions.PermisoPorPuesto, permissions.PermisoPorRol]  # o el que estés usando realmente
    filterset_fields = ['estudiante', 'tutor', 'estado']
    search_fields = ['motivo']

    def get_queryset(self):
        qs = super().get_queryset()

        user = self.request.user
        if not user or not user.is_authenticated:
           return qs  # devolver todo para usuarios anónimos

        if hasattr(user, 'superadmin') or hasattr(user, 'admin'):
           return qs

        if hasattr(user, 'tutor'):
           return qs.filter(tutor__usuario=user)

        if hasattr(user, 'estudiante'):
           return qs.filter(estudiante__usuario=user)

        return Licencia.objects.none()

    
    def get_permissions(self):
        if self.action in ['listar', 'crear','editar', 'eliminar', 'cambiar_estado']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action in ['crear', 'editar']:
            return CreateLicenciaSerializer
        return LicenciaSerializer

    @action(detail=False, methods=['get'], url_path='listar')
    def listar(self, request):
        qs = self.get_queryset()
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @csrf_exempt
    @action(detail=False, methods=['post'], url_path='crear')
    def crear(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            licencia = serializer.save()
        return Response(LicenciaSerializer(licencia).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['put'], url_path='editar')
    def editar(self, request, pk=None):
        licencia = self.get_object()
        serializer = UpdateEstadoLicenciaSerializer(licencia, data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
           licencia = serializer.save()
        return Response(LicenciaSerializer(licencia).data)

    @action(detail=True, methods=['delete'], url_path='eliminar')
    def eliminar(self, request, pk=None):
        licencia = self.get_object()
        licencia.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['patch'], url_path='cambiar-estado')
    def cambiar_estado(self, request, pk=None):
        licencia = self.get_object()
        nuevo_estado = request.data.get('estado')

        if nuevo_estado not in dict(Licencia.ESTADOS_LICENCIA):
            return Response({'error': 'Estado inválido.'}, status=status.HTTP_400_BAD_REQUEST)

        licencia.estado = nuevo_estado
        licencia.save()
        return Response({'mensaje': 'Estado actualizado correctamente.'})

class AsistenciaGeneralViewSet(viewsets.ModelViewSet):
    queryset = AsistenciaGeneral.objects.all()
    filterset_fields = ['estudiante', 'estado', 'fecha']
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CreateAsistenciaGeneralSerializer
        return AsistenciaGeneralSerializer

class AsistenciaClaseViewSet(viewsets.ModelViewSet):
    queryset = AsistenciaClase.objects.all()
    filterset_fields = ['clase', 'estudiante', 'estado', 'fecha'] 
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CreateAsistenciaClaseSerializer
        return AsistenciaClaseSerializer