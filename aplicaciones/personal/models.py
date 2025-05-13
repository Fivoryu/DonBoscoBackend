from django.db import models
from aplicaciones.usuarios.models import Usuario
from aplicaciones.academico.models import Materia

class Especialidad(models.Model):
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
        unique_together = ('nombre', 'materia')
    
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