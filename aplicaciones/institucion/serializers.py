from rest_framework import serializers
from django.db.models import Count, Q
from .models import Colegio, Modulo, Aula, UnidadEducativa

class ColegioSerializer(serializers.ModelSerializer):
    """Serializer para representar colegios base."""
    class Meta:
        model = Colegio
        fields = ['id', 'nombre', 'logo', 'direccion', 'telefono', 'email', 'sitio_web']

class CreateColegioSerializer(serializers.ModelSerializer):
    """Serializer para creación/edición de colegios."""
    class Meta:
        model = Colegio
        fields = ['nombre', 'logo', 'direccion', 'telefono', 'email', 'sitio_web', 'super_admin_fk']

class ModuloSerializer(serializers.ModelSerializer):
    """Serializer para representar módulos, incluyendo conteos de aulas y datos de colegio."""
    colegioId = serializers.IntegerField(source='colegio_fk_id', read_only=True)
    colegio = ColegioSerializer(source='colegio_fk', read_only=True)

    cantidad_aulas = serializers.IntegerField(read_only=True)  
    aulas_ocupadas = serializers.SerializerMethodField()
    aulas_disponibles = serializers.SerializerMethodField()

    class Meta:
        model = Modulo
        fields = [
            'id', 'nombre', 'descripcion', 'pisos',
            'cantidad_aulas', 'aulas_ocupadas', 'aulas_disponibles',
            'colegioId', 'colegio',
        ]

    def get_aulas_ocupadas(self, obj):
        return getattr(obj, 'aulas_ocupadas', obj.aulas.filter(estado=True).count())

    def get_aulas_disponibles(self, obj):
        total = getattr(obj, 'cantidad_aulas_real', obj.cantidad_aulas)
        ocupadas = getattr(obj, 'aulas_ocupadas', obj.aulas.filter(estado=True).count())
        disponibles = total - ocupadas
        return disponibles if disponibles >= 0 else 0

class CreateModuloSerializer(serializers.ModelSerializer):
    """Serializer para creación/edición de módulos."""
    class Meta:
        model = Modulo
        fields = ['nombre', 'descripcion', 'cantidad_aulas', 'pisos', 'colegio_fk']

class AulaSerializer(serializers.ModelSerializer):
    """Serializer para representar aulas, anidando módulo."""
    modulo = ModuloSerializer(read_only=True)

    class Meta:
        model = Aula
        fields = ['id', 'nombre', 'capacidad', 'estado', 'tipo', 'equipamiento', 'piso', 'modulo']

class CreateAulaSerializer(serializers.ModelSerializer):
    """Serializer para creación/edición de aulas."""
    class Meta:
        model = Aula
        fields = ['modulo', 'nombre', 'capacidad', 'estado', 'tipo', 'equipamiento', 'piso']

class UnidadEducativaSerializer(serializers.ModelSerializer):
    """Serializer para representar unidades educativas con colegio y administrador."""
    colegio = ColegioSerializer(read_only=True)

    class Meta:
        model = UnidadEducativa
        fields = [
            'id', 'codigo_sie', 'turno', 'nombre', 'direccion',
            'telefono', 'nivel', 'colegio'
        ]

class CreateUnidadEducativaSerializer(serializers.ModelSerializer):
    """Serializer para creación/edición de unidades educativas."""
    class Meta:
        model = UnidadEducativa
        fields = ['codigo_sie', 'turno', 'nombre', 'direccion', 'telefono', 'nivel', 'colegio']
