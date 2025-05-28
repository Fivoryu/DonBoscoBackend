from rest_framework import serializers
from .models import Grado, Paralelo, Curso, Materia, MateriaCurso, Clase
from aplicaciones.institucion.serializers import UnidadEducativaSerializer, AulaSerializer
from aplicaciones.institucion.models import Aula
from aplicaciones.personal.models import Profesor

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
    id = serializers.IntegerField(source='paralelo_id', read_only=True)
    paralelo = ParaleloSerializer(read_only=True)
    paralelo_id = serializers.PrimaryKeyRelatedField(
        queryset=Paralelo.objects.all(), source='paralelo', write_only=True
    )

    class Meta:
        model = Curso
        fields = ['id', 'paralelo', 'paralelo_id', 'nombre', 'tutor']

class MateriaCursoSerializer(serializers.ModelSerializer):
    materia = MateriaSerializer(read_only=True)
    curso = CursoSerializer(read_only=True)

    class Meta:
        model = MateriaCurso
        fields = ['id', 'curso', 'materia', 'profesor']

# Serializers para creación / edición
class CreateGradoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grado
        fields = ['id', 'unidad_educativa', 'nivel_educativo', 'numero']

class CreateParaleloSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paralelo
        fields = ['id', 'grado', 'letra']

class CreateCursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curso
        fields = ['id', 'paralelo', 'nombre', 'tutor']

class CreateMateriaCursoSerializer(serializers.ModelSerializer):
    curso   = serializers.PrimaryKeyRelatedField(queryset=Curso.objects.all())
    materia = serializers.PrimaryKeyRelatedField(queryset=Materia.objects.all())
    profesor = serializers.PrimaryKeyRelatedField(
        queryset=Profesor.objects.all(),
        allow_null=True,
        required=False,
    )

    class Meta:
        model  = MateriaCurso
        fields = ['id', 'curso', 'materia', 'profesor']

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

