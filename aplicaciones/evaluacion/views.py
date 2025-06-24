from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import (
    DimensionEvaluacion,
    Actividad,
    NotaActividad,
    NotaFinalMateria,
    AutoEvaluacion
)
from .serializers import (
    DimensionEvaluacionSerializer,
    ActividadSerializer,
    NotaActividadSerializer,
    NotaFinalMateriaSerializer,
    AutoEvaluacionSerializer,
    CreateActividadSerializer,
    CreateNotaActividadSerializer,
    CreateNotaFinalMateriaSerializer,
    CreateAutoEvaluacionSerializer,
    CreateDimensionEvaluacionSerializer,
)

class DimensionEvaluacionViewSet(viewsets.ModelViewSet):
    queryset = DimensionEvaluacion.objects.all()
    serializer_class = DimensionEvaluacionSerializer
    filterset_fields = ['periodo', 'tipo']
    search_fields = ['nombre']
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CreateDimensionEvaluacionSerializer
        return DimensionEvaluacionSerializer

class ActividadViewSet(viewsets.ModelViewSet):
    queryset = Actividad.objects.all()
    serializer_class = ActividadSerializer
    filterset_fields = [
        'materia_curso', 
        'profesor', 
        'dimension',
        'es_recuperacion',
        'activa'
    ]
    search_fields = ['nombre', 'descripcion']
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CreateActividadSerializer
        return ActividadSerializer
    
    @action(detail=True, methods=['get'])
    def notas(self, request, pk=None):
        actividad = self.get_object()
        notas = actividad.notas.all()
        serializer = NotaActividadSerializer(notas, many=True)
        return Response(serializer.data)

class NotaActividadViewSet(viewsets.ModelViewSet):
    queryset = NotaActividad.objects.all()
    serializer_class = NotaActividadSerializer
    filterset_fields = ['actividad', 'estudiante']
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CreateNotaActividadSerializer
        return NotaActividadSerializer

class NotaFinalMateriaViewSet(viewsets.ModelViewSet):
    queryset = NotaFinalMateria.objects.all()
    serializer_class = NotaFinalMateriaSerializer
    filterset_fields = ['estudiante', 'materia_curso', 'periodo', 'estado']

    def get_queryset(self):
        queryset = super().get_queryset()
        anio = self.request.query_params.get('anio')

        if anio:
            queryset = queryset.filter(periodo__calendario__año=anio)

        return queryset

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CreateNotaFinalMateriaSerializer
        return NotaFinalMateriaSerializer

class AutoEvaluacionViewSet(viewsets.ModelViewSet):
    queryset = AutoEvaluacion.objects.all()
    serializer_class = AutoEvaluacionSerializer
    filterset_fields = [
        'estudiante', 
        'materia_curso', 
        'periodo', 
        'dimension'
    ]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CreateAutoEvaluacionSerializer
        return AutoEvaluacionSerializer