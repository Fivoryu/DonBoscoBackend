from django.db import models
from aplicaciones.estudiantes.models import Estudiante, Tutor
from aplicaciones.academico.models import Clase
from django.core.validators import MinValueValidator, MaxValueValidator

class Comportamiento(models.Model):
    TIPOS_COMPORTAMIENTO = [
        ('POS', 'Positivo'),
        ('NEG', 'Negativo'),
        ('OBS', 'Observación'),
    ]
    
    estudiante = models.ForeignKey(
        Estudiante,
        on_delete=models.CASCADE,
        related_name='comportamientos'
    )
    fecha = models.DateField()
    descripcion = models.TextField()
    tipo = models.CharField(
        max_length=3,
        choices=TIPOS_COMPORTAMIENTO
    )
    gravedad = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    class Meta:
        verbose_name = 'Registro de Comportamiento'
        verbose_name_plural = 'Registros de Comportamiento'
        db_table = 'comportamiento'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.estudiante} ({self.fecha})"

class Licencia(models.Model):
    ESTADOS_LICENCIA = [
        ('SOL', 'Solicitada'),
        ('APR', 'Aprobada'),
        ('REC', 'Rechazada'),
        ('FIN', 'Finalizada'),
    ]
    
    estudiante = models.ForeignKey(
        Estudiante,
        on_delete=models.CASCADE,
        related_name='licencias'
    )
    tutor = models.ForeignKey(
        Tutor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='licencias'
    )
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    motivo = models.TextField()
    estado = models.CharField(
        max_length=3,
        choices=ESTADOS_LICENCIA,
        default='SOL'
    )
    archivo = models.FileField(
        upload_to='licencias/',
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name = 'Licencia'
        verbose_name_plural = 'Licencias'
        db_table = 'licencia'
        ordering = ['-fecha_inicio']
    
    def __str__(self):
        return f"Licencia {self.estudiante} ({self.fecha_inicio} a {self.fecha_fin})"

class AsistenciaGeneral(models.Model):
    ESTADOS_ASISTENCIA = [
        ('ASI', 'Asistió'),
        ('FAL', 'Faltó'),
        ('TAR', 'Tardanza'),
        ('JUS', 'Falta justificada'),
    ]
    
    estudiante = models.ForeignKey(
        Estudiante,
        on_delete=models.CASCADE,
        related_name='asistencias_generales'
    )
    fecha = models.DateField()
    estado = models.CharField(
        max_length=3,
        choices=ESTADOS_ASISTENCIA
    )
    hora_entrada = models.TimeField(null=True, blank=True)
    hora_salida = models.TimeField(null=True, blank=True)
    observaciones = models.TextField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Asistencia General'
        verbose_name_plural = 'Asistencias Generales'
        db_table = 'asistencia_general'
        unique_together = ('estudiante', 'fecha')
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.estudiante} - {self.fecha}: {self.get_estado_display()}"

class AsistenciaClase(models.Model):
    ESTADOS_ASISTENCIA_CLASE = [
        ('ASI', 'Presente'),
        ('FAL', 'Ausente'),
        ('TAR', 'Tardanza'),
        ('LIC', 'Con licencia'),
    ]
    
    clase = models.ForeignKey(
        Clase,
        on_delete=models.CASCADE,
        related_name='asistencias'
    )
    estudiante = models.ForeignKey(
        Estudiante,
        on_delete=models.CASCADE,
        related_name='asistencias_clases'
    )
    fecha = models.DateField()
    hora = models.TimeField()
    estado = models.CharField(
        max_length=3,
        choices=ESTADOS_ASISTENCIA_CLASE
    )
    licencia = models.ForeignKey(
        Licencia,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='asistencias'
    )
    
    class Meta:
        verbose_name = 'Asistencia por Clase'
        verbose_name_plural = 'Asistencias por Clases'
        db_table = 'asistencia_clase'
        unique_together = ('clase', 'estudiante', 'fecha')
        ordering = ['-fecha', 'hora']
    
    def __str__(self):
        return f"{self.estudiante} - {self.clase}: {self.get_estado_display()}"