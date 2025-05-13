from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from aplicaciones.academico.models import MateriaCurso
from aplicaciones.personal.models import Profesor
from aplicaciones.estudiantes.models import Estudiante
from aplicaciones.calendario.models import Periodo

class DimensionEvaluacion(models.Model):
    TIPOS_DIMENSION = [
        ('EXA', 'Examen'),
        ('TAR', 'Tarea'),
        ('PRO', 'Proyecto'),
        ('PAR', 'Participación'),
        ('OTR', 'Otro'),
    ]
    
    periodo = models.ForeignKey(
        Periodo,
        on_delete=models.CASCADE,
        related_name='dimensiones'
    )
    nombre = models.CharField(max_length=50)
    tipo = models.CharField(
        max_length=3,
        choices=TIPOS_DIMENSION,
        default='OTR'
    )
    ponderacion = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    
    class Meta:
        verbose_name = 'Dimensión de Evaluación'
        verbose_name_plural = 'Dimensiones de Evaluación'
        db_table = 'dimension_evaluacion'
        unique_together = ('periodo', 'nombre')
    
    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()}) - {self.ponderacion}%"

class Actividad(models.Model):
    materia_curso = models.ForeignKey(
        MateriaCurso,
        on_delete=models.CASCADE,
        related_name='actividades'
    )
    profesor = models.ForeignKey(
        Profesor,
        on_delete=models.CASCADE,
        related_name='actividades'
    )
    dimension = models.ForeignKey(
        DimensionEvaluacion,
        on_delete=models.CASCADE,
        related_name='actividades'
    )
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    fecha = models.DateField()
    fecha_entrega = models.DateField(blank=True, null=True)
    nota_maxima = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    es_recuperacion = models.BooleanField(default=False)
    activa = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Actividad'
        verbose_name_plural = 'Actividades'
        db_table = 'actividad'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.nombre} - {self.materia_curso}"

class NotaActividad(models.Model):
    actividad = models.ForeignKey(
        Actividad,
        on_delete=models.CASCADE,
        related_name='notas'
    )
    estudiante = models.ForeignKey(
        Estudiante,
        on_delete=models.CASCADE,
        related_name='notas_actividades'
    )
    nota_obtenida = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)
    comentario = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Nota de Actividad'
        verbose_name_plural = 'Notas de Actividades'
        db_table = 'nota_actividad'
        unique_together = ('actividad', 'estudiante')
    
    def __str__(self):
        return f"{self.estudiante} - {self.actividad}: {self.nota_obtenida}"

class NotaFinalMateria(models.Model):
    estudiante = models.ForeignKey(
        Estudiante,
        on_delete=models.CASCADE,
        related_name='notas_finales'
    )
    materia_curso = models.ForeignKey(
        MateriaCurso,
        on_delete=models.CASCADE,
        related_name='notas_finales'
    )
    periodo = models.ForeignKey(
        Periodo,
        on_delete=models.CASCADE,
        related_name='notas_finales'
    )
    nota_final = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    estado = models.CharField(
        max_length=3,
        choices=[('APR', 'Aprobado'), ('REP', 'Reprobado'), ('INC', 'Incompleto')],
        default='INC'
    )
    fecha_calculo = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Nota Final de Materia'
        verbose_name_plural = 'Notas Finales de Materias'
        db_table = 'nota_final_materia'
        unique_together = ('estudiante', 'materia_curso', 'periodo')
    
    def __str__(self):
        return f"{self.estudiante} - {self.materia_curso}: {self.nota_final}"

class AutoEvaluacion(models.Model):
    estudiante = models.ForeignKey(
        Estudiante,
        on_delete=models.CASCADE,
        related_name='auto_evaluaciones'
    )
    materia_curso = models.ForeignKey(
        MateriaCurso,
        on_delete=models.CASCADE,
        related_name='auto_evaluaciones'
    )
    periodo = models.ForeignKey(
        Periodo,
        on_delete=models.CASCADE,
        related_name='auto_evaluaciones'
    )
    dimension = models.ForeignKey(
        DimensionEvaluacion,
        on_delete=models.CASCADE,
        related_name='auto_evaluaciones'
    )
    nota = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    comentario = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Autoevaluación'
        verbose_name_plural = 'Autoevaluaciones'
        db_table = 'auto_evaluacion'
        unique_together = ('estudiante', 'materia_curso', 'periodo', 'dimension')
    
    def __str__(self):
        return f"AutoEval: {self.estudiante} - {self.dimension}: {self.nota}"