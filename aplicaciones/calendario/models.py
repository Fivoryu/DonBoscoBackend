from django.db import models
from aplicaciones.institucion.models import UnidadEducativa  # Asumiendo que existe esta app

class CalendarioAcademico(models.Model):
    unidad_educativa = models.ForeignKey(
        UnidadEducativa,
        on_delete=models.CASCADE,
        related_name='calendarios'
    )
    año = models.PositiveSmallIntegerField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    activo = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Calendario Académico'
        verbose_name_plural = 'Calendarios Académicos'
        db_table = 'calendario_academico'
        unique_together = ('unidad_educativa', 'año')
        ordering = ['-año']
    
    def __str__(self):
        return f"Calendario {self.año} - {self.unidad_educativa}"

class Periodo(models.Model):
    TIPOS_DIVISION = [
        ('SEM', 'Semestre'),
        ('TRI', 'Trimestre'),
        ('BIM', 'Bimestre'),
        ('CUA', 'Cuatrimestre'),
        ('OTR', 'Otro'),
    ]
    
    ESTADOS = [
        ('PLA', 'Planificado'),
        ('CUR', 'En Curso'),
        ('FIN', 'Finalizado'),
        ('CAN', 'Cancelado'),
    ]
    
    calendario = models.ForeignKey(
        CalendarioAcademico,
        on_delete=models.CASCADE,
        related_name='periodos'
    )
    tipo_division = models.CharField(
        max_length=3,
        choices=TIPOS_DIVISION
    )
    nombre = models.CharField(max_length=50)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    estado = models.CharField(
        max_length=3,
        choices=ESTADOS,
        default='PLA'
    )
    
    class Meta:
        verbose_name = 'Periodo Académico'
        verbose_name_plural = 'Periodos Académicos'
        db_table = 'periodo'
        ordering = ['fecha_inicio']
    
    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_division_display()}) - {self.calendario.año}"

class TipoFeriado(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    es_nacional = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Tipo de Feriado'
        verbose_name_plural = 'Tipos de Feriados'
        db_table = 'tipo_feriado'
    
    def __str__(self):
        return f"{self.nombre} {'(Nacional)' if self.es_nacional else ''}"

class Feriado(models.Model):
    calendario = models.ForeignKey(
        CalendarioAcademico,
        on_delete=models.CASCADE,
        related_name='feriados'
    )
    tipo = models.ForeignKey(
        TipoFeriado,
        on_delete=models.PROTECT,
        related_name='feriados'
    )
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    fecha = models.DateField()
    
    class Meta:
        verbose_name = 'Feriado'
        verbose_name_plural = 'Feriados'
        db_table = 'feriado'
        ordering = ['fecha']
    
    def __str__(self):
        return f"{self.nombre} - {self.fecha}"

class TipoHorario(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True, null=True)
    turno = models.CharField(
        max_length=10,
        choices=[('MAÑANA', 'Mañana'), ('TARDE', 'Tarde'), ('NOCHE', 'Noche')]
    )
    
    class Meta:
        verbose_name = 'Tipo de Horario'
        verbose_name_plural = 'Tipos de Horarios'
        db_table = 'tipo_horario'
    
    def __str__(self):
        return f"{self.nombre} ({self.turno})"

class Horario(models.Model):
    DIAS_SEMANA = [
        ('LUN', 'Lunes'),
        ('MAR', 'Martes'),
        ('MIE', 'Miércoles'),
        ('JUE', 'Jueves'),
        ('VIE', 'Viernes'),
        ('SAB', 'Sábado'),
        ('DOM', 'Domingo'),
    ]
    
    tipo = models.ForeignKey(
        TipoHorario,
        on_delete=models.PROTECT,
        related_name='horarios'
    )
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    dia = models.CharField(
        max_length=3,
        choices=DIAS_SEMANA
    )
    
    class Meta:
        verbose_name = 'Horario'
        verbose_name_plural = 'Horarios'
        db_table = 'horario'
        ordering = ['dia', 'hora_inicio']
    
    def __str__(self):
        return f"{self.get_dia_display()} {self.hora_inicio}-{self.hora_fin}"

class ClaseHorario(models.Model):
    clase = models.ForeignKey(
        'academico.Clase',  # Asumiendo que existe en la app academico
        on_delete=models.CASCADE,
        related_name='horarios'
    )
    horario = models.ForeignKey(
        Horario,
        on_delete=models.CASCADE,
        related_name='clases'
    )
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Horario de Clase'
        verbose_name_plural = 'Horarios de Clases'
        db_table = 'clase_horario'
        unique_together = ('clase', 'horario')
    
    def __str__(self):
        return f"{self.clase} - {self.horario}"