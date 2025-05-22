from rest_framework import serializers
from .models import Grado, Paralelo, Curso, Materia, MateriaCurso

class MateriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Materia
        fields = '__all__'

class GradoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grado
        fields = '__all__'

class ParaleloSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paralelo
        fields = '__all__'

class CursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curso
        fields = '__all__'

class MateriaCursoSerializer(serializers.ModelSerializer):
    materia = MateriaSerializer()
    curso = CursoSerializer()
    
    class Meta:
        model = MateriaCurso
        fields = '__all__'

class CreateGradoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grado
        fields = '__all__'
