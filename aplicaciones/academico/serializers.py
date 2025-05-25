from rest_framework import serializers
from .models import Grado, Paralelo, Curso, Materia, MateriaCurso, Clase
from aplicaciones.institucion.serializers import UnidadEducativaSerializer, AulaSerializer
from aplicaciones.institucion.models import Aula

class MateriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Materia
        fields = ['id', 'nombre']

class GradoSerializer(serializers.ModelSerializer):
    unidad_educativa = UnidadEducativaSerializer(read_only=True)
    nivel_educativo_display = serializers.CharField(source='get_nivel_educativo_display', read_only=True)
    nombre = serializers.CharField(read_only=True)  # Usando property del modelo

    class Meta:
        model = Grado
        fields = [
            'id',
            'unidad_educativa',
            'nivel_educativo',
            'nivel_educativo_display',
            'numero',
            'nombre',
        ]

class ParaleloSerializer(serializers.ModelSerializer):
    grado = GradoSerializer(read_only=True)
    grado_id = serializers.PrimaryKeyRelatedField(
        queryset=Grado.objects.all(), source='grado', write_only=True
    )
    nombre = serializers.SerializerMethodField()

    class Meta:
        model = Paralelo
        fields = ['id', 'grado', 'grado_id', 'letra', 'nombre']

    def get_nombre(self, obj):
        return f"{obj.grado.nombre} - Paralelo {obj.letra}"

class CursoSerializer(serializers.ModelSerializer):
    paralelo = ParaleloSerializer(read_only=True)
    paralelo_id = serializers.PrimaryKeyRelatedField(
        queryset=Paralelo.objects.all(), source='paralelo', write_only=True
    )

    class Meta:
        model = Curso
        fields = ['paralelo', 'paralelo_id', 'nombre']

class MateriaCursoSerializer(serializers.ModelSerializer):
    materia = MateriaSerializer(read_only=True)
    materia_id = serializers.PrimaryKeyRelatedField(
        queryset=Materia.objects.all(), source='materia', write_only=True
    )
    curso = CursoSerializer(read_only=True)
    curso_id = serializers.PrimaryKeyRelatedField(
        queryset=Curso.objects.all(), source='curso', write_only=True
    )

    class Meta:
        model = MateriaCurso
        fields = ['id', 'curso', 'curso_id', 'materia', 'materia_id']

# Serializers para creación / edición
class CreateGradoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grado
        fields = ['unidad_educativa', 'nivel_educativo', 'numero']

class CreateParaleloSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paralelo
        fields = ['grado', 'letra']

class CreateCursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curso
        fields = ['paralelo', 'nombre']

class CreateMateriaCursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MateriaCurso
        fields = ['curso', 'materia']

class ClaseSerializer(serializers.ModelSerializer):
    materia_curso = MateriaCursoSerializer(read_only=True)
    materia_curso_id = serializers.PrimaryKeyRelatedField(
        queryset=MateriaCurso.objects.all(),
        source='materia_curso',
        write_only=True
    )
    aula = AulaSerializer(read_only=True)
    aula_id = serializers.PrimaryKeyRelatedField(
        queryset=Aula.objects.all(),
        source='aula',
        write_only=True
    )

    class Meta:
        model = Clase
        fields = ['id', 'materia_curso', 'materia_curso_id', 'aula', 'aula_id']

