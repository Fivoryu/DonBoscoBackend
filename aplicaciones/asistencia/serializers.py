from rest_framework import serializers
from .models import (
    Comportamiento,
    Licencia,
    AsistenciaGeneral,
    AsistenciaClase
)
from aplicaciones.estudiantes.serializers import EstudianteSerializer, TutorSerializer
from aplicaciones.academico.serializers import ClaseSerializer

# Serializadores de lectura (anidados)
class ComportamientoSerializer(serializers.ModelSerializer):
    estudiante = EstudianteSerializer(read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    gravedad_display = serializers.SerializerMethodField()

    class Meta:
        model = Comportamiento
        fields = '__all__'

    def get_gravedad_display(self, obj):
        return f"{obj.gravedad}/5"

class LicenciaSerializer(serializers.ModelSerializer):
    estudiante = EstudianteSerializer(read_only=True)
    tutor = TutorSerializer(read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)

    class Meta:
        model = Licencia
        fields = '__all__'

class AsistenciaGeneralSerializer(serializers.ModelSerializer):
    estudiante = EstudianteSerializer(read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)

    class Meta:
        model = AsistenciaGeneral
        fields = '__all__'

class AsistenciaClaseSerializer(serializers.ModelSerializer):
    clase = ClaseSerializer(read_only=True)
    estudiante = EstudianteSerializer(read_only=True)
    licencia = LicenciaSerializer(read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)

    class Meta:
        model = AsistenciaClase
        fields = '__all__'

# Serializadores de escritura (solo IDs)
class CreateComportamientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comportamiento
        fields = '__all__'

class CreateLicenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Licencia
        fields = '__all__'

class CreateAsistenciaGeneralSerializer(serializers.ModelSerializer):
    class Meta:
        model = AsistenciaGeneral
        fields = '__all__'

class CreateAsistenciaClaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = AsistenciaClase
        fields = '__all__'