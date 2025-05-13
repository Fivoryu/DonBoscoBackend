from django.db import models
from django.core.validators import MinValueValidator
from aplicaciones.usuarios.models import Admin, SuperAdmin
class Colegio(models.Model):
    nombre = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='colegios/logos/', null=True, blank=True)
    direccion = models.TextField()
    telefono = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    sitio_web = models.URLField(blank=True, null=True)
    super_admin_fk= models.ForeignKey(
        SuperAdmin,
        on_delete=models.SET_NULL,
        related_name='colegios',
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name = 'Colegio'
        verbose_name_plural = 'Colegios'
        db_table = 'colegio'
    
    def __str__(self):
        return self.nombre

class Modulo(models.Model):
    nombre = models.CharField(max_length=100)
    cantidad_aulas = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
    descripcion = models.TextField(blank=True, null=True)
    colegio_fk = models.ForeignKey(
        Colegio,
        on_delete=models.SET_NULL,
        related_name='modulos',
        null=True,
        blank=True
    )

    
    
    class Meta:
        verbose_name = 'Módulo'
        verbose_name_plural = 'Módulos'
        db_table = 'modulo'
    
    def __str__(self):
        return f"{self.nombre} ({self.cantidad_aulas} aulas)"

class Aula(models.Model):
    TIPOS_AULA = [
        ('AUL', 'Aula Regular'),
        ('LAB', 'Laboratorio'),
        ('TAL', 'Taller'),
        ('AUD', 'Auditorio'),
        ('COM', 'Sala de Computación'),
        ('GIM', 'Gimnasio'),
        ('BIB', 'Biblioteca'),
    ]
    
    modulo = models.ForeignKey(
        Modulo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='aulas'
    )
    nombre = models.CharField(max_length=50)
    capacidad = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
    estado = models.BooleanField(default=True)
    
    tipo = models.CharField(
        max_length=3,
        choices=TIPOS_AULA,
        default='AUL'
    )
    equipamiento = models.TextField(blank=True, null=True)
    piso = models.PositiveSmallIntegerField(default=1)
    
    class Meta:
        verbose_name = 'Aula'
        verbose_name_plural = 'Aulas'
        db_table = 'aula'
        unique_together = ('modulo', 'nombre')
    
    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()}) - Módulo {self.modulo}"

class UnidadEducativa(models.Model):
    TURNOS = [
        ('MAÑANA', 'Mañana'),
        ('TARDE', 'Tarde'),
        ('NOCHE', 'Noche'),
        ('COMPLETO', 'Jornada Completa'),
    ]
    
    
    codigo_sie = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Código SIE'
    )
    turno = models.CharField(
        max_length=10,
        choices=TURNOS
    )
    nombre= models.CharField(max_length=100,blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    nivel = models.CharField(max_length=50,blank=True, null=True)
    admin_fk = models.ForeignKey(
        Admin,
        on_delete=models.SET_NULL,
        related_name='unidades_educativas',
        null=True,
        blank=True
    )
    colegio = models.ForeignKey(
        Colegio,
        on_delete=models.SET_NULL,
        related_name='unidades_educativas',
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name = 'Unidad Educativa'
        verbose_name_plural = 'Unidades Educativas'
        db_table = 'unidad_educativa'
    
    def __str__(self):
        return f"{self.colegio} - Turno {self.get_turno_display()}"