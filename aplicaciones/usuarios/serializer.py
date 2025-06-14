from rest_framework import serializers
from .models import Usuario, Rol, Notificacion, Bitacora, SuperAdmin, Puesto, Admin, Accion, ModeloPermitido, PermisoPuesto, PermisoRol
from django.contrib.auth.hashers import make_password
from django.apps import apps as models
from aplicaciones.institucion.models import UnidadEducativa, Colegio
from aplicaciones.institucion.serializers import ColegioSerializer

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

class PuestoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Puesto
        fields = ['id', 'nombre', 'descripcion']
        read_only_fields = ['id']

class AdminSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer(read_only=True)
    usuario_id = serializers.PrimaryKeyRelatedField(
        queryset=Usuario.objects.all(),
        source='usuario',
        write_only=True
    )
    puesto = PuestoSerializer(read_only=True)
    puesto_id = serializers.PrimaryKeyRelatedField(
        queryset=Puesto.objects.all(),
        source='puesto',
        write_only=True,
        required=False,
        allow_null=True
    )
    # Cambia unidad a read_only y agrega unidad_id para escritura
    unidad = serializers.SerializerMethodField(read_only=True)
    unidad_id = serializers.PrimaryKeyRelatedField(
        queryset=UnidadEducativa.objects.all(),
        source='unidad',
        write_only=True,
        required=False,
        allow_null=True
    )

    def get_unidad(self, obj):
        if obj.unidad:
            # Devuelve todos los campos relevantes de la unidad educativa, incluyendo el colegio anidado
            return {
                "id": obj.unidad.id,
                "nombre": obj.unidad.nombre,
                "codigo_sie": obj.unidad.codigo_sie,
                "turno": obj.unidad.turno,
                "direccion": obj.unidad.direccion,
                "telefono": obj.unidad.telefono,
                "nivel": obj.unidad.nivel,
                "colegio": ColegioSerializer(obj.unidad.colegio).data if obj.unidad.colegio else None,
            }
        return None

    class Meta:
        model = Admin
        fields = [
            'usuario_id', 'usuario',
            'puesto_id', 'puesto',
            'unidad_id', 'unidad',
            'estado'
        ]

class AccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Accion
        fields = ['id', 'nombre']

class ModeloPermitidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModeloPermitido
        fields = ['id', 'nombre']

class PermisoRolSerializer(serializers.ModelSerializer):
    rol = serializers.PrimaryKeyRelatedField(read_only=True)
    modelo = serializers.PrimaryKeyRelatedField(read_only=True)
    accion = serializers.PrimaryKeyRelatedField(read_only=True)
    rol_nombre    = serializers.CharField(source='rol.nombre', read_only=True)
    modelo_nombre = serializers.CharField(source='modelo.nombre', read_only=True)
    accion_nombre = serializers.CharField(source='accion.nombre', read_only=True)

    rol_id = serializers.PrimaryKeyRelatedField(
        queryset=Rol.objects.all(),
        source='rol',
        write_only=True
    )
    modelo_id = serializers.PrimaryKeyRelatedField(
        queryset=ModeloPermitido.objects.all(),
        source='modelo',
        write_only=True
    )
    accion_id = serializers.PrimaryKeyRelatedField(
        queryset=Accion.objects.all(),
        source='accion',
        write_only=True
    )

    class Meta:
        model  = PermisoRol
        fields = [
            'id',
            'rol', 'rol_id', 'rol_nombre',
            'modelo', 'modelo_id', 'modelo_nombre',
            'accion', 'accion_id', 'accion_nombre',
        ]

class PermisoPuestoSerializer(serializers.ModelSerializer):
    puesto = PuestoSerializer(read_only=True)
    puesto_id = serializers.PrimaryKeyRelatedField(
        queryset=Puesto.objects.all(),
        source='puesto',
        write_only=True
    )
    modelo = ModeloPermitidoSerializer(read_only=True)
    modelo_id = serializers.PrimaryKeyRelatedField(
        queryset=ModeloPermitido.objects.all(),
        source='modelo',
        write_only=True
    )
    accion = AccionSerializer(read_only=True)
    accion_id = serializers.PrimaryKeyRelatedField(
        queryset=Accion.objects.all(),
        source='accion',
        write_only=True
    )

    class Meta:
        model = PermisoPuesto
        fields = ['id', 'puesto', 'puesto_id', 'modelo', 'modelo_id', 'accion', 'accion_id']