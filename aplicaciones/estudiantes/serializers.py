# aplicaciones/personal/serializers.py
from rest_framework import serializers
from aplicaciones.usuarios.models import Usuario
from aplicaciones.academico.models import Curso
from .models import Estudiante, Tutor, TutorEstudiante

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'ci', 'nombre', 'apellido', 'sexo', 'email', 'fecha_nacimiento', 'username']

class CursoSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curso
        fields = ['paralelo_id', 'nombre']  # asumiendo que usas paralelo como pk

# --- Estudiante ---
class EstudianteSerializer(serializers.ModelSerializer):
    usuario   = UsuarioSerializer(read_only=True)
    curso     = CursoSimpleSerializer(read_only=True)

    class Meta:
        model  = Estudiante
        fields = ['usuario', 'rude', 'estado', 'curso']

class CreateEstudianteSerializer(serializers.ModelSerializer):
    usuario_id = serializers.PrimaryKeyRelatedField(
        queryset=Usuario.objects.all(),
        source='usuario',
        write_only=True
    )
    curso_id = serializers.PrimaryKeyRelatedField(
        queryset=Curso.objects.all(),
        source='curso',
        allow_null=True,
        required=False,
        write_only=True
    )

    class Meta:
        model  = Estudiante
        fields = ['usuario_id', 'rude', 'estado', 'curso_id']

# --- Tutor ---
class TutorSerializer(serializers.ModelSerializer):
    usuario     = UsuarioSerializer(read_only=True)
    parentesco_display = serializers.CharField(source='get_parentesco_display', read_only=True)

    class Meta:
        model  = Tutor
        fields = ['usuario', 'parentesco', 'parentesco_display']

class CreateTutorSerializer(serializers.ModelSerializer):
    usuario_id = serializers.PrimaryKeyRelatedField(
        queryset=Usuario.objects.all(),
        source='usuario',
        write_only=True
    )

    class Meta:
        model  = Tutor
        fields = ['usuario_id', 'parentesco']

# --- TutorEstudiante ---
class TutorEstudianteSerializer(serializers.ModelSerializer):
    tutor      = TutorSerializer(read_only=True)
    estudiante = EstudianteSerializer(read_only=True)

    class Meta:
        model  = TutorEstudiante
        fields = ['id', 'tutor', 'estudiante', 'fecha_asignacion', 'es_principal']

class CreateTutorEstudianteSerializer(serializers.ModelSerializer):
    tutor_id      = serializers.PrimaryKeyRelatedField(
        queryset=Tutor.objects.all(),
        source='tutor',
        write_only=True
    )
    estudiante_id = serializers.PrimaryKeyRelatedField(
        queryset=Estudiante.objects.all(),
        source='estudiante',
        write_only=True
    )

    class Meta:
        model  = TutorEstudiante
        fields = ['tutor_id', 'estudiante_id', 'es_principal']
