from django.db import models
from aplicaciones.usuarios.models import Usuario
from aplicaciones.academico.models import Materia, Grado
from aplicaciones.calendario.models import Periodo

class Especialidad(models.Model):
    grado = models.ForeignKey(
        Grado,
        on_delete=models.CASCADE,
        related_name='especialidad',
        null=True,   
        blank=True    
    )
    nombre = models.CharField(max_length=100)
    materia = models.ForeignKey(
        Materia,
        on_delete=models.CASCADE,
        related_name='especialidades'
    )
    
    class Meta:
        verbose_name = 'Especialidad'
        verbose_name_plural = 'Especialidades'
        db_table = 'especialidad'
        unique_together = ('grado', 'materia')
    
    def __str__(self):
        return f"{self.nombre} ({self.materia})"

class Profesor(models.Model):
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='profesor'
    )
    estado = models.BooleanField(default=True)
    unidad = models.ForeignKey(
        'institucion.UnidadEducativa',
        on_delete=models.PROTECT,
        related_name="profesores",
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name = 'Profesor'
        verbose_name_plural = 'Profesores'
        db_table = 'profesor'
    
    def __str__(self):
        return str(self.usuario)

class ProfesorEspecialidad(models.Model):
    profesor = models.ForeignKey(
        Profesor,
        on_delete=models.CASCADE,
        related_name='especialidades'
    )
    especialidad = models.ForeignKey(
        Especialidad,
        on_delete=models.CASCADE,
        related_name='profesores'
    )
    fecha_asignacion = models.DateField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Especialidad de Profesor'
        verbose_name_plural = 'Especialidades de Profesores'
        db_table = 'profesor_especialidad'
        unique_together = ('profesor', 'especialidad')
        ordering = ['-fecha_asignacion']
    
    def __str__(self):
        return f"{self.profesor} - {self.especialidad}"

class CargaHoraria(models.Model):
    profesor_especialidad = models.ForeignKey(
        ProfesorEspecialidad,
        on_delete=models.CASCADE,
        related_name='cargas_horarias',
        null=True,   
        blank=True  
    )
    horas = models.PositiveSmallIntegerField()
    periodo = models.ForeignKey(
        Periodo,
        on_delete=models.PROTECT,
        related_name='cargas_horarias',
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name = 'Carga Horaria'
        verbose_name_plural = 'Cargas Horarias'
        db_table = 'carga_horaria'
        constraints = [
            models.UniqueConstraint(
                fields=['profesor_especialidad', 'periodo'],
                name='unique_profesor_especialidad_periodo'
            )
        ]
        ordering = ['-periodo', '-horas']

    def __str__(self):
        return f"{self.profesor_especialidad} - {self.horas}h"