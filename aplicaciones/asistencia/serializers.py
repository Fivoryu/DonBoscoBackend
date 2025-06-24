from rest_framework import serializers

from aplicaciones.estudiantes.models import Estudiante, Tutor
from .models import (
    Comportamiento,
    Licencia,
    AsistenciaGeneral,
    AsistenciaClase
)
from aplicaciones.estudiantes.serializers import EstudianteSerializer, TutorSerializer
from aplicaciones.academico.serializers import ClaseSerializer

class ComportamientoSerializer(serializers.ModelSerializer):
    estudiante = EstudianteSerializer()
    
    class Meta:
        model = Comportamiento
        fields = '__all__'

class LicenciaSerializer(serializers.ModelSerializer):
    estudiante = EstudianteSerializer()
    tutor = TutorSerializer()
    
    class Meta:
        model = Licencia
        fields = '__all__'

class AsistenciaGeneralSerializer(serializers.ModelSerializer):
    estudiante = EstudianteSerializer()
    
    class Meta:
        model = AsistenciaGeneral
        fields = '__all__'

class AsistenciaClaseSerializer(serializers.ModelSerializer):
    clase = ClaseSerializer()
    estudiante = EstudianteSerializer()
    licencia = LicenciaSerializer()
    
    class Meta:
        model = AsistenciaClase
        fields = '__all__'

# Serializers para creación/actualización
class CreateComportamientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comportamiento
        fields = '__all__'

class CreateLicenciaSerializer(serializers.ModelSerializer):
    tutor = serializers.PrimaryKeyRelatedField(
        queryset=Tutor.objects.all(),
        required=False,
        allow_null=True
    )
    estudiante = serializers.PrimaryKeyRelatedField(queryset=Estudiante.objects.all())

    class Meta:
        model = Licencia
        fields = ['estudiante', 'tutor', 'fecha_inicio', 'fecha_fin', 'motivo', 'archivo']

    def validate(self, attrs):
        # Validación opcional: que la fecha de fin sea posterior a la de inicio
        if attrs['fecha_inicio'] > attrs['fecha_fin']:
            raise serializers.ValidationError("La fecha de fin debe ser posterior a la fecha de inicio.")
        return attrs

class UpdateEstadoLicenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Licencia
        fields = ['estado']

class CreateAsistenciaGeneralSerializer(serializers.ModelSerializer):
    class Meta:
        model = AsistenciaGeneral
        fields = '__all__'

class CreateAsistenciaClaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = AsistenciaClase
        fields = '__all__'