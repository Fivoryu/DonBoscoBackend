from django.contrib import admin
from .models import (
    Comportamiento,
    Licencia,
    AsistenciaGeneral,
    AsistenciaClase
)

@admin.register(Comportamiento)
class ComportamientoAdmin(admin.ModelAdmin):
    list_display = ('estudiante', 'fecha', 'tipo', 'get_tipo_display', 'gravedad')
    list_filter = ('tipo', 'gravedad', 'fecha')
    search_fields = ('estudiante__usuario__nombre', 'descripcion')
    date_hierarchy = 'fecha'
    autocomplete_fields = ['estudiante']

@admin.register(Licencia)
class LicenciaAdmin(admin.ModelAdmin):
    list_display = ('estudiante', 'fecha_inicio', 'fecha_fin', 'estado', 'get_estado_display', 'tutor')
    list_filter = ('estado', 'fecha_inicio', 'fecha_fin', 'tutor')
    search_fields = ('estudiante__usuario__nombre', 'motivo', 'tutor__usuario__nombre')
    date_hierarchy = 'fecha_inicio'
    autocomplete_fields = ['estudiante', 'tutor']

@admin.register(AsistenciaGeneral)
class AsistenciaGeneralAdmin(admin.ModelAdmin):
    list_display = ('estudiante', 'fecha', 'estado', 'get_estado_display', 'hora_entrada', 'hora_salida')
    list_filter = ('estado', 'fecha')
    search_fields = ('estudiante__usuario__nombre',)
    date_hierarchy = 'fecha'
    autocomplete_fields = ['estudiante']

@admin.register(AsistenciaClase)
class AsistenciaClaseAdmin(admin.ModelAdmin):
    list_display = ('estudiante', 'clase', 'fecha', 'hora', 'estado', 'get_estado_display', 'licencia')
    list_filter = ('clase', 'estado', 'fecha')
    search_fields = ('estudiante__usuario__nombre', 'clase__nombre')
    date_hierarchy = 'fecha'
    autocomplete_fields = ['estudiante', 'clase', 'licencia']