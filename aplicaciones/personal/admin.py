from django.contrib import admin
from .models import Profesor, Especialidad, ProfesorEspecialidad, CargaHoraria

class ProfesorEspecialidadInline(admin.TabularInline):
    model = ProfesorEspecialidad
    extra = 1

@admin.register(Profesor)
class ProfesorAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'estado')
    list_filter = ('estado',)
    search_fields = ('usuario__nombre', 'usuario__apellido')
    inlines = [ProfesorEspecialidadInline]

@admin.register(Especialidad)
class EspecialidadAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'materia')
    list_filter = ('materia',)
    search_fields = ('nombre', 'materia__nombre')

@admin.register(ProfesorEspecialidad)
class ProfesorEspecialidadAdmin(admin.ModelAdmin):
    list_display = ('profesor', 'especialidad', 'fecha_asignacion')
    list_filter = ('especialidad', 'fecha_asignacion')
    search_fields = ('profesor__usuario__nombre', 'especialidad__nombre')

@admin.register(CargaHoraria)
class CargaHorariaAdmin(admin.ModelAdmin):
    list_display = (
        'get_profesor',
        'get_especialidad',
        'get_unidad',
        'horas',
        'periodo',
    )
    list_filter = ('profesor_especialidad__especialidad', 'profesor_especialidad__profesor__unidad', 'periodo')
    search_fields = (
        'profesor_especialidad__profesor__usuario__nombre',
        'profesor_especialidad__especialidad__nombre',
        'profesor_especialidad__profesor__unidad__nombre'
    )

    def get_profesor(self, obj):
        return obj.profesor_especialidad.profesor.usuario
    get_profesor.short_description = 'Profesor'

    def get_especialidad(self, obj):
        return obj.profesor_especialidad.especialidad.nombre
    get_especialidad.short_description = 'Especialidad'

    def get_unidad(self, obj):
        return obj.profesor_especialidad.profesor.unidad
    get_unidad.short_description = 'Unidad Educativa'