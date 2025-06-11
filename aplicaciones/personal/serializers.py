from rest_framework import serializers
from aplicaciones.institucion.serializers import UnidadEducativaSerializer
from aplicaciones.academico.serializers import MateriaSerializer, GradoSerializer
from aplicaciones.usuarios.serializer import UsuarioSerializer
from .models import Especialidad, Profesor, ProfesorEspecialidad, CargaHoraria
from aplicaciones.usuarios.models import Usuario
from aplicaciones.institucion.models import UnidadEducativa
from rest_framework.validators import UniqueTogetherValidator
from aplicaciones.calendario.serializers import PeriodoSerializer


class EspecialidadSerializer(serializers.ModelSerializer):
    materia = MateriaSerializer(read_only=True)
    grado   = GradoSerializer(read_only=True)

    class Meta:
        model = Especialidad
        fields = ['id', 'nombre', 'materia', 'grado']


class CreateEspecialidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Especialidad
        fields = ['nombre', 'materia', 'grado']
        validators = [
            UniqueTogetherValidator(
                queryset=Especialidad.objects.all(),
                fields=['grado', 'materia'],
                message="Ya existe una especialidad para este grado y materia."
            )
        ]


class ProfesorSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer(read_only=True)
    unidad = UnidadEducativaSerializer(read_only=True)

    class Meta:
        model = Profesor
        fields = ['usuario', 'estado', 'unidad']


class CreateProfesorSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer()
    unidad = serializers.PrimaryKeyRelatedField(
        queryset=UnidadEducativa.objects.all(),
        required=False,
        allow_null=True,
        default=None
    )

    class Meta:
        model = Profesor
        fields = ['usuario', 'estado', 'unidad']

    def create(self, validated_data):
        user_data = validated_data.pop('usuario')
        user = Usuario.objects.create_user(**user_data)
        # Si unidad no está en validated_data, pásalo como None
        unidad = validated_data.pop('unidad', None)
        return Profesor.objects.create(usuario=user, unidad=unidad, **validated_data)

class UpdateProfesorSerializer(serializers.ModelSerializer):
    ci               = serializers.CharField(source='usuario.ci', required=True)
    foto             = serializers.CharField(source='usuario.foto', required=False, allow_null=True)
    nombre           = serializers.CharField(source='usuario.nombre', required=True)
    apellido         = serializers.CharField(source='usuario.apellido', required=True)
    sexo             = serializers.CharField(source='usuario.sexo', required=True)
    email            = serializers.EmailField(source='usuario.email', required=True)
    fecha_nacimiento = serializers.DateField(source='usuario.fecha_nacimiento', required=False, allow_null=True)
    username         = serializers.CharField(source='usuario.username', required=True)
    estado           = serializers.BooleanField(required=False)
    unidad           = serializers.PrimaryKeyRelatedField(
        queryset=UnidadEducativa.objects.all(),
        required=False,
        allow_null=True,
        default=None
    )

    class Meta:
        model = Profesor
        fields = [
            'ci','foto','nombre','apellido','sexo',
            'email','fecha_nacimiento','username',
            'estado','unidad',
        ]

    def update(self, instance, validated_data):
        user_data = validated_data.pop('usuario', {})
        user = instance.usuario
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()
        if 'estado' in validated_data:
            instance.estado = validated_data['estado']
        # Permitir null en unidad
        if 'unidad' in validated_data:
            instance.unidad = validated_data['unidad']
        instance.save()
        return instance


class ProfesorEspecialidadSerializer(serializers.ModelSerializer):
    profesor = ProfesorSerializer(read_only=True)
    especialidad = EspecialidadSerializer(read_only=True)

    class Meta:
        model = ProfesorEspecialidad
        fields = ['id', 'profesor', 'especialidad', 'fecha_asignacion']


class CreateProfesorEspecialidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfesorEspecialidad
        fields = ['profesor', 'especialidad']


class CargaHorariaSerializer(serializers.ModelSerializer):
    profesor_especialidad = serializers.PrimaryKeyRelatedField(read_only=True)
    profesor = serializers.SerializerMethodField()
    especialidad = serializers.SerializerMethodField()
    periodo = PeriodoSerializer(read_only=True)

    class Meta:
        model = CargaHoraria
        fields = ['id', 'profesor_especialidad', 'profesor', 'especialidad', 'horas', 'periodo']

    def get_profesor(self, obj):
        # Devuelve el profesor serializado
        return ProfesorSerializer(obj.profesor_especialidad.profesor).data if obj.profesor_especialidad else None

    def get_especialidad(self, obj):
        # Devuelve la especialidad serializada
        return EspecialidadSerializer(obj.profesor_especialidad.especialidad).data if obj.profesor_especialidad else None

class CreateCargaHorariaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CargaHoraria
        fields = ['profesor_especialidad', 'horas', 'periodo']
        validators = [
            UniqueTogetherValidator(
                queryset=CargaHoraria.objects.all(),
                fields=['profesor_especialidad', 'periodo'],
                message="Ya existe una carga horaria para este profesor, especialidad y periodo."
            )
        ]