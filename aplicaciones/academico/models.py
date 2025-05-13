from django.db import models
from aplicaciones.institucion.models import UnidadEducativa, Aula  # Asumiendo que existe esta app

class Clase(models.Model):
    curso = models.ForeignKey(
        'Curso', 
        on_delete=models.CASCADE,
        verbose_name='Curso relacionado'
    )
    aula = models.ForeignKey(
        Aula, 
        on_delete=models.CASCADE,
        verbose_name='Aula asignada'
    )

    class Meta:
        verbose_name = 'Clase'
        verbose_name_plural = 'Clases'
        db_table = 'clase'  # Optional: to keep the same table name as in your SQL

    def __str__(self):
        return f"Clase {self.id} - Curso: {self.curso}, Aula: {self.aula}"

class Grado(models.Model):
    NIVELES_EDUCATIVOS = [
        ('INI', 'Educación Inicial'),
        ('PRI', 'Educación Primaria'),
        ('SEC', 'Educación Secundaria'),
    ]
    
    unidad_educativa = models.ForeignKey(
        UnidadEducativa,
        on_delete=models.CASCADE,
        related_name='grados'
    )
    nivel_educativo = models.CharField(
        max_length=3,
        choices=NIVELES_EDUCATIVOS
    )
    
    class Meta:
        verbose_name = 'Grado'
        verbose_name_plural = 'Grados'
        db_table = 'grado'
        unique_together = ('unidad_educativa', 'nivel_educativo')
    
    def __str__(self):
        return f"{self.get_nivel_educativo_display()} - {self.unidad_educativa}"

class Paralelo(models.Model):
    grado = models.ForeignKey(
        Grado,
        on_delete=models.CASCADE,
        related_name='paralelos'
    )
    letra = models.CharField(max_length=1)
    capacidad_maxima = models.PositiveIntegerField()
    
    class Meta:
        verbose_name = 'Paralelo'
        verbose_name_plural = 'Paralelos'
        db_table = 'paralelo'
        unique_together = ('grado', 'letra')
        ordering = ['letra']
    
    def __str__(self):
        return f"{self.grado} - Paralelo {self.letra}"

class Curso(models.Model):
    paralelo = models.OneToOneField(
        Paralelo,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='curso'
    )
    nombre = models.CharField(max_length=100)
    
    class Meta:
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'
        db_table = 'curso'
    
    def __str__(self):
        return f"{self.nombre} - {self.paralelo}"

class Materia(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    
    class Meta:
        verbose_name = 'Materia'
        verbose_name_plural = 'Materias'
        db_table = 'materia'
    
    def __str__(self):
        return self.nombre

class MateriaCurso(models.Model):
    curso = models.ForeignKey(
        Curso,
        on_delete=models.CASCADE,
        related_name='materias'
    )
    materia = models.ForeignKey(
        Materia,
        on_delete=models.CASCADE,
        related_name='cursos'
    )
    
    class Meta:
        verbose_name = 'Materia por Curso'
        verbose_name_plural = 'Materias por Curso'
        db_table = 'materia_curso'
        unique_together = ('curso', 'materia')
    
    def __str__(self):
        return f"{self.materia} en {self.curso}"