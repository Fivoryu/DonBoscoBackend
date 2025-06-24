from rest_framework import serializers

from aplicaciones.institucion.models import UnidadEducativa
from .models import (
  CalendarioAcademico,
  Periodo,
  TipoFeriado,
  Feriado,
  TipoHorario,
  Horario,
  ClaseHorario
)

class PeriodoSerializer(serializers.ModelSerializer):
  tipo_division_display = serializers.CharField(
    source='get_tipo_division_display', read_only=True
  )
  estado_display = serializers.CharField(
    source='get_estado_display', read_only=True
  )

  class Meta:
    model = Periodo
    fields = [
      'id', 'calendario', 'tipo_division', 'tipo_division_display',
      'nombre', 'fecha_inicio', 'fecha_fin', 'estado', 'estado_display'
    ]

class FeriadoSerializer(serializers.ModelSerializer):
  tipo_nombre = serializers.CharField(
    source='tipo.nobmre', read_only=True
  )
  tipo_es_nacional = serializers.BooleanField(
    source='tipo.es_nacional', read_only=True
  )

  class Meta:
    model = Feriado
    fields = [
      'id', 'calendario', 'tipo', 'tipo_nombre', 'tipo_es_nacional',
      'nombre', 'descripcion', 'fecha'
    ]

from aplicaciones.institucion.serializers import UnidadEducativaSerializer

class CalendarioAcademicoSerializer(serializers.ModelSerializer):
    unidad_educativa = serializers.PrimaryKeyRelatedField(
        queryset=UnidadEducativa.objects.all()    
    )
    unidad_educativa_nombre = serializers.CharField(
        source='unidad_educativa.nombre', read_only=True
    )
    periodos = PeriodoSerializer(many=True, read_only=True)
    feriados = FeriadoSerializer(many=True, read_only=True)

    class Meta:
        model = CalendarioAcademico
        fields = [
            'id', 'unidad_educativa', 'unidad_educativa_nombre',
            'año', 'fecha_inicio', 'fecha_fin', 'activo',
            'periodos', 'feriados'
        ]


class TipoFeriadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoFeriado
        fields = '__all__'

class TipoHorarioSerializer(serializers.ModelSerializer):
    turno_display = serializers.CharField(
        source='get_turno_display', read_only=True
    )

    class Meta:
        model = TipoHorario
        fields = ['id', 'nombre', 'descripcion', 'turno', 'turno_display']

class HorarioSerializer(serializers.ModelSerializer):
    dia_display = serializers.CharField(
        source='get_dia_display', read_only=True
    )
    tipo_nombre = serializers.CharField(
        source='tipo.nombre', read_only=True
    )
    tipo_turno_display = serializers.CharField(
        source='tipo.get_turno_display', read_only=True
    )

    class Meta:
        model = Horario
        fields = [
            'id', 'tipo', 'tipo_nombre', 'tipo_turno_display',
            'hora_inicio', 'hora_fin', 'dia', 'dia_display'
        ]

class ClaseHorarioSerializer(serializers.ModelSerializer):
    clase_id = serializers.PrimaryKeyRelatedField(
        source='clase', read_only=True
    )
    horario_id = serializers.PrimaryKeyRelatedField(
        source='horario', read_only=True
    )

    class Meta:
        model = ClaseHorario
        fields = ['id', 'clase', 'horario', 'fecha_inicio', 'fecha_fin']