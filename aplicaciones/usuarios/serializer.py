from rest_framework import serializers
from .models import Usuario, Rol, Notificacion, Bitacora
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate

class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = ['id', 'nombre', 'descripcion']
        read_only_fields = ['id']
        extra_kwargs = {
            'nombre': {'required': True, 'allow_blank': False},
            'descripcion': {'required': False}
        }

    def validate_nombre(self, data):
        """
        Valida que el nombre del rol sea único (insensible a mayúsculas)
        """
        nombre = data.get('nombre', '').strip()
        if self.instance and self.instance.nombre.lower() == data.lower():
            return data
            
        if Rol.objects.filter(nombre__iexact=data).exists():
            raise serializers.ValidationError({"nombre": "Ya existe un rol con este nombre"})
        return data

class UsuarioSerializer(serializers.ModelSerializer):
    rol = serializers.PrimaryKeyRelatedField(
        queryset=Rol.objects.all(),
        required=True
    )
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'ci', 'username', 'email', 'nombre', 'apellido',
            'edad', 'foto', 'telefono', 'rol', 'rol_id', 'is_active',
            'date_joined', 'password'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'is_active': {'read_only': True},
            'date_joined': {'read_only': True}
        }
    
    def create(self, validated_data):
        """
        Sobrescribe el método create para encriptar la contraseña.
        """
        validated_data['password'] = make_password(validated_data.get('password'))
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Sobrescribe el método update para encriptar la contraseña.
        """
        password = validated_data.pop('password', None)
        if password:
            validated_data['password'] = make_password(password)
        return super().update(instance, validated_data)

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """
        Valida las credenciales del usuario.
        """
        username = data.get('username')
        password = data.get('password')

        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError("Credenciales inválidas")
        if not user.is_active:
            raise serializers.ValidationError("Cuenta desactivada")
        
        data['user'] = user
        return data

class NotificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacion
        fields = ['id', 'usuario', 'mensaje', 'leida', 'fecha']
        extra_kwargs = {
            'usuario': {'read_only': True},
            'leida': {'default': False},
            'fecha': {'read_only': True}
        }
        read_only_fields = ('fecha', 'usuario')

class BitacoraSerializer(serializers.ModelSerializer):
    usuario = serializers.StringRelatedField()
    
    class Meta:
        model = Bitacora
        fields = ['id', 'usuario', 'hora_entrada', 'hora_salida']
        read_only_fields = ['hora_entrada', 'hora_salida']
