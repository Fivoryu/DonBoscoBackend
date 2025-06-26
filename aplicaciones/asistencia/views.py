from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
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
from aplicaciones.usuarios.permissions import PermisoPorRol, PermisoPorPuesto, PermisoEstudianteView
from aplicaciones.usuarios.authentication import MultiTokenAuthentication

class ComportamientoViewSet(viewsets.ModelViewSet):
    queryset = Comportamiento.objects.select_related('estudiante').all()
    filterset_fields = ['estudiante', 'tipo', 'fecha']
    search_fields = ['descripcion', 'estudiante__usuario__nombre']
    permission_classes = [PermisoPorRol | PermisoPorPuesto]
    authentication_classes = [MultiTokenAuthentication]
    ordering_fields = ['fecha', 'gravedad']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CreateComportamientoSerializer
        return ComportamientoSerializer

    @action(detail=False, methods=['get'], url_path='listar')
    def listar(self, request):
        return self.list(request)

    @action(detail=True, methods=['get'], url_path='detalle')
    def detalle(self, request, pk=None):
        return self.retrieve(request, pk=pk)

    @action(detail=False, methods=['post'], url_path='crear')
    def crear(self, request):
        return self.create(request)

    @action(detail=True, methods=['put', 'patch'], url_path='actualizar')
    def actualizar(self, request, pk=None):
        return self.partial_update(request, pk=pk)

    @action(detail=True, methods=['delete'], url_path='eliminar')
    def eliminar(self, request, pk=None):
        return self.destroy(request, pk=pk)

class LicenciaViewSet(viewsets.ModelViewSet):
    queryset = Licencia.objects.select_related('estudiante', 'tutor').all()
    filterset_fields = ['estudiante', 'tutor', 'estado', 'fecha_inicio', 'fecha_fin']
    search_fields = ['motivo', 'estudiante__usuario__nombre', 'tutor__usuario__nombre']
    permission_classes = [PermisoPorRol | PermisoPorPuesto]
    authentication_classes = [MultiTokenAuthentication]
    ordering_fields = ['fecha_inicio', 'fecha_fin']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CreateLicenciaSerializer
        return LicenciaSerializer

    @action(detail=False, methods=['get'], url_path='listar')
    def listar(self, request):
        return self.list(request)

    @action(detail=True, methods=['get'], url_path='detalle')
    def detalle(self, request, pk=None):
        return self.retrieve(request, pk=pk)

    @action(detail=False, methods=['post'], url_path='crear')
    def crear(self, request):
        return self.create(request)

    @action(detail=True, methods=['put', 'patch'], url_path='actualizar')
    def actualizar(self, request, pk=None):
        return self.partial_update(request, pk=pk)

    @action(detail=True, methods=['delete'], url_path='eliminar')
    def eliminar(self, request, pk=None):
        return self.destroy(request, pk=pk)

class AsistenciaGeneralViewSet(viewsets.ModelViewSet):
    queryset = AsistenciaGeneral.objects.select_related('estudiante').all()
    filterset_fields = ['estudiante', 'estado', 'fecha']
    search_fields = ['estudiante__usuario__nombre']
    permission_classes = [PermisoPorRol | PermisoPorPuesto]
    authentication_classes = [MultiTokenAuthentication]
    ordering_fields = ['fecha']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CreateAsistenciaGeneralSerializer
        return AsistenciaGeneralSerializer

    @action(detail=False, methods=['get'], url_path='listar')
    def listar(self, request):
        return self.list(request)

    @action(detail=True, methods=['get'], url_path='detalle')
    def detalle(self, request, pk=None):
        return self.retrieve(request, pk=pk)

    @action(detail=False, methods=['post'], url_path='crear')
    def crear(self, request):
        return self.create(request)

    @action(detail=True, methods=['put', 'patch'], url_path='actualizar')
    def actualizar(self, request, pk=None):
        return self.partial_update(request, pk=pk)

    @action(detail=True, methods=['delete'], url_path='eliminar')
    def eliminar(self, request, pk=None):
        return self.destroy(request, pk=pk)
    
    def create(self, request, *args, **kwargs):
        print("DATA RECIBIDA:", request.data)
        is_many = isinstance(request.data, list)
        serializer = self.get_serializer(data=request.data, many=is_many)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            print("ERRORES DE SERIALIZER:", serializer.errors)
            raise
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class AsistenciaClaseViewSet(viewsets.ModelViewSet):
    queryset = AsistenciaClase.objects.select_related('clase', 'estudiante', 'licencia').all()
    filterset_fields = ['clase', 'estudiante', 'estado', 'fecha']
    search_fields = ['clase__nombre', 'estudiante__usuario__nombre']
    permission_classes = [PermisoPorRol | PermisoPorPuesto]
    authentication_classes = [MultiTokenAuthentication]
    ordering_fields = ['fecha', 'hora']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CreateAsistenciaClaseSerializer
        return AsistenciaClaseSerializer

    @action(detail=False, methods=['get'], url_path='listar')
    def listar(self, request):
        return self.list(request)

    @action(detail=True, methods=['get'], url_path='detalle')
    def detalle(self, request, pk=None):
        return self.retrieve(request, pk=pk)

    @action(detail=False, methods=['post'], url_path='crear')
    def crear(self, request):
        return self.create(request)

    @action(detail=True, methods=['put', 'patch'], url_path='actualizar')
    def actualizar(self, request, pk=None):
        return self.partial_update(request, pk=pk)

    @action(detail=True, methods=['delete'], url_path='eliminar')
    def eliminar(self, request, pk=None):
        return self.destroy(request, pk=pk)