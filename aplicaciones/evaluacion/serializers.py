from rest_framework import serializers
from .models import (
    DimensionEvaluacion,
    Actividad,
    NotaActividad,
    NotaFinalMateria,
    AutoEvaluacion
)
from aplicaciones.academico.serializers import MateriaCursoSerializer
from aplicaciones.personal.serializers import ProfesorSerializer
from aplicaciones.estudiantes.serializers import EstudianteSerializer
from aplicaciones.calendario.serializers import PeriodoSerializer

class DimensionEvaluacionSerializer(serializers.ModelSerializer):
    periodo = PeriodoSerializer()
    
    class Meta:
        model = DimensionEvaluacion
        fields = '__all__'

class ActividadSerializer(serializers.ModelSerializer):
    materia_curso = MateriaCursoSerializer()
    profesor = ProfesorSerializer()
    dimension = DimensionEvaluacionSerializer()
    
    class Meta:
        model = Actividad
        fields = '__all__'

class NotaActividadSerializer(serializers.ModelSerializer):
    actividad = ActividadSerializer()
    estudiante = EstudianteSerializer()
    
    class Meta:
        model = NotaActividad
        fields = '__all__'

class NotaFinalMateriaSerializer(serializers.ModelSerializer):
    estudiante = EstudianteSerializer()
    materia_curso = MateriaCursoSerializer()
    periodo = PeriodoSerializer()
    
    class Meta:
        model = NotaFinalMateria
        fields = '__all__'

class AutoEvaluacionSerializer(serializers.ModelSerializer):
    estudiante = EstudianteSerializer()
    materia_curso = MateriaCursoSerializer()
    periodo = PeriodoSerializer()
    dimension = DimensionEvaluacionSerializer()
    
    class Meta:
        model = AutoEvaluacion
        fields = '__all__'

# Serializers para creación/actualización
class CreateActividadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actividad
        fields = '__all__'

class CreateNotaActividadSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotaActividad
        fields = '__all__'

class CreateNotaFinalMateriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotaFinalMateria
        fields = '__all__'

class CreateAutoEvaluacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutoEvaluacion
        fields = '__all__'