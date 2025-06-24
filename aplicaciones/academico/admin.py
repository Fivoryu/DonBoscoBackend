from django.contrib import admin
from .models import Grado, Paralelo, Curso, Materia, MateriaCurso, Clase

@admin.register(Grado)
class GradoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'unidad_educativa', 'nivel_educativo', 'numero')
    list_filter = ('unidad_educativa', 'nivel_educativo')
    search_fields = ('unidad_educativa__nombre',)
    ordering = ('unidad_educativa', 'nivel_educativo', 'numero')

@admin.register(Paralelo)
class ParaleloAdmin(admin.ModelAdmin):
    list_display = ('grado', 'letra')
    list_filter = ('grado__unidad_educativa', 'grado__nivel_educativo')
    search_fields = ('grado__unidad_educativa__nombre', 'grado__nivel_educativo')
    ordering = ('grado', 'letra')

@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'paralelo', 'tutor')
    list_filter = ('paralelo__grado__unidad_educativa',)
    search_fields = ('nombre', 'paralelo__grado__unidad_educativa__nombre')
    autocomplete_fields = ['paralelo', 'tutor']

@admin.register(Materia)
class MateriaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(MateriaCurso)
class MateriaCursoAdmin(admin.ModelAdmin):
    list_display = ('materia', 'curso', 'profesor')
    list_filter = ('curso__paralelo__grado__unidad_educativa',)
    search_fields = ('materia__nombre', 'curso__nombre', 'profesor__usuario__nombre')
    autocomplete_fields = ['curso', 'materia', 'profesor']

@admin.register(Clase)
class ClaseAdmin(admin.ModelAdmin):
    list_display = ('materia_curso', 'aula')
    list_filter = ('materia_curso__curso__paralelo__grado__unidad_educativa',)
    search_fields = ('materia_curso__materia__nombre', 'materia_curso__curso__nombre', 'aula__nombre')
    autocomplete_fields = ['materia_curso', 'aula']
