from rest_framework import serializers
from .models import Usuario, Rol, Notificacion, Bitacora
from django.contrib.auth.hashers import make_password
from .models import SuperAdmin

class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = ['id', 'nombre', 'descripcion']
        read_only_fields = ['id']
        extra_kwargs = {
            'nombre': {'required': True, 'allow_blank': False},
            'descripcion': {'required': False}
        }

    def validate_nombre(self, value):
        """
        Valida que el nombre del rol sea único (insensible a mayúsculas)
        """
        if self.instance and self.instance.nombre.lower() == value.lower():
            return value
            
        if Rol.objects.filter(nombre__iexact=value).exists():
            raise serializers.ValidationError("Ya existe un rol con este nombre")
        return value

class UsuarioSerializer(serializers.ModelSerializer):
    rol = RolSerializer(read_only=True)
    rol_id = serializers.PrimaryKeyRelatedField(
        queryset=Rol.objects.all(),
        source='rol',
        write_only=True
    )
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'ci', 'username', 'email', 'nombre', 'apellido',
             'foto', 'telefono', 'fecha_nacimiento', 'sexo', 'rol_id', 'rol', 'is_active',
            'date_joined','password'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'is_active': {'read_only': True},
            'date_joined': {'read_only': True}
        }
    
    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data.get('password'))
        return super().create(validated_data)

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

class NotificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacion
        fields = '__all__'
        read_only_fields = ('fecha', 'usuario')

class BitacoraSerializer(serializers.ModelSerializer):
    # Assign current authenticated user automatically
    usuario = serializers.HiddenField(default=serializers.CurrentUserDefault())
    hora_entrada = serializers.DateTimeField(read_only=True)
    fecha = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Bitacora
        fields = [
            'id',
            'usuario',
            'hora_entrada',
            'hora_salida',
            'ip',
            'tabla_afectada',
            'accion',
            'descripcion',
            'fecha',
        ]
        read_only_fields = ['id']

class SuperAdminSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer(read_only=True)

    class Meta:
        model = SuperAdmin
        fields = ['usuario_id', 'usuario']