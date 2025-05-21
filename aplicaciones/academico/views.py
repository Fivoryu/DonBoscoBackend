from rest_framework import viewsets
from .models import Grado, Paralelo, Curso, Materia, MateriaCurso
from .serializers import (
    GradoSerializer,
    ParaleloSerializer,
    CursoSerializer,
    MateriaSerializer,
    MateriaCursoSerializer
)

from aplicaciones.usuarios.utils import registrar_bitacora
from aplicaciones.usuarios.usuario_views import get_client_ip 
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from aplicaciones.usuarios.permissions import IsSuperAdmin

class GradoViewSet(viewsets.ModelViewSet):
    queryset = Grado.objects.all()
    serializer_class = GradoSerializer
    filterset_fields = ['unidad_educativa', 'nivel_educativo']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update', 'crear_grado', 'editar_grado']:
            return CreateGradoSerializer
        return GradoSerializer

    @action(detail=False, methods=['get'], url_path='cantidad')
    def obtener_cantidad_grados(self, request):
        cantidad = Grado.objects.count()
        registrar_bitacora(
            usuario=request.user,
            ip=get_client_ip(request),
            tabla_afectada='grado',
            accion='ver',
            descripcion='Consultó la cantidad de grados'
        )
        return Response({'cantidad_grados': cantidad}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='crear')
    def crear_grado(self, request):
        serializer = CreateGradoSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            """            registrar_bitacora(
                usuario=request.user,
                ip=get_client_ip(request),
                tabla_afectada='grado',
                accion='crear',
                descripcion='Creó un grado'
            )
            """

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['put'], url_path='editar')
    def editar_grado(self, request, pk=None):
        try:
            grado = Grado.objects.get(pk=pk)
        except Grado.DoesNotExist:
            return Response({'detail': 'Grado no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CreateGradoSerializer(grado, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            """
            registrar_bitacora(
                usuario=request.user,
                ip=get_client_ip(request),
                tabla_afectada='grado',
                accion='editar',
                descripcion=f'Editó el grado {pk}'
            )
            """
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'], url_path='eliminar')
    def eliminar_grado(self, request, pk=None):
        try:
            grado = Grado.objects.get(pk=pk)
        except Grado.DoesNotExist:
            return Response({'detail': 'Grado no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        grado.delete()
        """        registrar_bitacora(
            usuario=request.user,
            ip=get_client_ip(request),
            tabla_afectada='grado',
            accion='eliminar',
            descripcion=f'Eliminó el grado {pk}'
        )
        """

        return Response({'detail': 'Grado eliminado correctamente.'}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='listar')
    def listar_grados(self, request):
        grados = self.filter_queryset(self.get_queryset())
        serializer = GradoSerializer(grados, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ParaleloViewSet(viewsets.ModelViewSet):
    queryset = Paralelo.objects.all()
    serializer_class = ParaleloSerializer
    filterset_fields = ['grado', 'letra']

class CursoViewSet(viewsets.ModelViewSet):
    queryset = Curso.objects.all()
    serializer_class = CursoSerializer
    filterset_fields = ['paralelo']

class MateriaViewSet(viewsets.ModelViewSet):
    queryset = Materia.objects.all()
    serializer_class = MateriaSerializer
    filterset_fields = ['nombre']
    search_fields = ['nombre']

class MateriaCursoViewSet(viewsets.ModelViewSet):
    queryset = MateriaCurso.objects.all()
    serializer_class = MateriaCursoSerializer
    filterset_fields = ['curso', 'materia']
