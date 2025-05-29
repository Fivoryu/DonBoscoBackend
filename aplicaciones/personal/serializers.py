from rest_framework import serializers
from aplicaciones.academico.serializers import MateriaSerializer, GradoSerializer
from aplicaciones.usuarios.serializer import UsuarioSerializer
from .models import Especialidad, Profesor, ProfesorEspecialidad
from aplicaciones.usuarios.models import Usuario
from rest_framework.validators import UniqueTogetherValidator


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

    class Meta:
        model = Profesor
        fields = ['usuario', 'estado']


class CreateProfesorSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer()

    class Meta:
        model = Profesor
        fields = ['usuario', 'estado']

    def create(self, validated_data):
        user_data = validated_data.pop('usuario')
        user = Usuario.objects.create_user(**user_data)
        return Profesor.objects.create(usuario=user, **validated_data)
    
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

    class Meta:
        model = Profesor
        # No incluimos password ni rol_id: sólo lo que de verdad queremos editar
        fields = [
            'ci','foto','nombre','apellido','sexo',
            'email','fecha_nacimiento','username',
            'estado',
        ]

    def update(self, instance, validated_data):
        # 1) Extraemos los datos de usuario
        user_data = validated_data.pop('usuario', {})
        user = instance.usuario

        # 2) Actualizamos sólo los atributos permitidos
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()

        # 3) Actualizamos el propio Profesor
        if 'estado' in validated_data:
            instance.estado = validated_data['estado']
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
