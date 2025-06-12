from django.db import models
from aplicaciones.institucion.models import UnidadEducativa, Aula  # Asumiendo que existe esta app
from django.core.validators import MinValueValidator, MaxValueValidator



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
    numero = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(6)],
        default=1,                          # <— aquí
        help_text="Número de grado dentro del nivel (1 a 6)"
    )

    class Meta:
        verbose_name = 'Grado'
        verbose_name_plural = 'Grados'
        db_table = 'grado'
        unique_together = ('unidad_educativa', 'nivel_educativo', 'numero')

    @property
    def nombre(self) -> str:
        # Mapea 1→'1ro', 2→'2do', 3→'3ro', 4→'4to', 5→'5to', 6→'6to'
        sufijos = {1: 'ro',   2: 'do', 3: 'ro',
                   4: 'to',   5: 'to', 6: 'to'}
        suf = sufijos.get(self.numero, '°')
        nivel = self.get_nivel_educativo_display()
        return f"{self.numero}{suf} de {nivel}"

    def __str__(self):
        return self.nombre

class Paralelo(models.Model):
    grado = models.ForeignKey(
        Grado,
        on_delete=models.CASCADE,
        related_name='paralelos'
    )
    letra = models.CharField(max_length=1)
    # capacidad_maxima = models.PositiveIntegerField()
    
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

    tutor = models.ForeignKey(
        'personal.Profesor',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cursos_tutorados'
    )
    
    class Meta:
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'
        db_table = 'curso'
    
    def __str__(self):
        tutor_str = f" (Tutor: {self.tutor})" if self.tutor else ""
        return f"{self.nombre} - {self.paralelo}{tutor_str}"

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

    profesor = models.ForeignKey(
        'personal.Profesor',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='materias_impartidas'
    )
    
    class Meta:
        verbose_name = 'Materia por Curso'
        verbose_name_plural = 'Materias por Curso'
        db_table = 'materia_curso'
        unique_together = ('curso', 'materia')
    
    def __str__(self):
        prof = f" — Prof.: {self.profesor}" if self.profesor else ""
        return f"{self.materia} en {self.curso}{prof}"
    


    
class Clase(models.Model):
    # Apunta ahora a MateriaCurso en lugar de Curso
    materia_curso = models.ForeignKey(
        MateriaCurso,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='clases',
        verbose_name='Materia en Curso'
    )
    aula = models.ForeignKey(
        Aula,
        on_delete=models.CASCADE,
        related_name='clases',
        verbose_name='Aula asignada'
    )

    class Meta:
        verbose_name = 'Clase'
        verbose_name_plural = 'Clases'
        db_table = 'clase'

    def __str__(self):
        # Muestro la materia y el curso a través de la relación intermedia
        return f"{self.materia_curso.materia.nombre} en {self.materia_curso.curso.nombre} — Aula {self.aula.nombre}"    