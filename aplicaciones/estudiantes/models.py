from django.db import models
from aplicaciones.usuarios.models import Usuario
from aplicaciones.academico.models import Curso

PARENTESCOS = [
    ('PAD', 'Padre'),
    ('MAD', 'Madre'),
    ('TUT', 'Tutor Legal'),
    ('HER', 'Hermano/a'),
    ('OTR', 'Otro'),
]

class Estudiante(models.Model):

    
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='estudiante'
    )
    rude = models.CharField(max_length=50, unique=True)
    estado = models.BooleanField(default=True)
    curso = models.ForeignKey(
        Curso,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='estudiantes'
    )
    
    class Meta:
        verbose_name = 'Estudiante'
        verbose_name_plural = 'Estudiantes'
        db_table = 'estudiante'
        ordering = ['usuario__apellido', 'usuario__nombre']
    
    def __str__(self):
        return f"{self.usuario} - {self.rude}"

class Tutor(models.Model):
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='tutor'
    )
    parentesco = models.CharField(
        max_length=3,
        choices=PARENTESCOS,
        default='OTR'
    )
    
    class Meta:
        verbose_name = 'Tutor'
        verbose_name_plural = 'Tutores'
        db_table = 'tutor'
        ordering = ['usuario__apellido', 'usuario__nombre']
    
    def __str__(self):
        return f"{self.usuario} ({self.get_parentesco_display()})"

class TutorEstudiante(models.Model):
    tutor = models.ForeignKey(
        Tutor,
        on_delete=models.CASCADE,
        related_name='estudiantes'
    )
    estudiante = models.ForeignKey(
        Estudiante,
        on_delete=models.CASCADE,
        related_name='tutores'
    )
    fecha_asignacion = models.DateField(auto_now_add=True)
    es_principal = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Relación Tutor-Estudiante'
        verbose_name_plural = 'Relaciones Tutor-Estudiante'
        db_table = 'tutor_estudiante'
        unique_together = ('tutor', 'estudiante')
        ordering = ['-es_principal', 'fecha_asignacion']
    
    def __str__(self):
        tipo = "Principal" if self.es_principal else "Secundario"
        return f"{self.tutor} -> {self.estudiante} ({tipo})"