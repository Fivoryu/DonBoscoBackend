from rest_framework import viewsets
from .models import Grado, Paralelo, Curso, Materia, MateriaCurso
from .serializers import (
    GradoSerializer,
    ParaleloSerializer,
    CursoSerializer,
    MateriaSerializer,
    MateriaCursoSerializer,
    CreateGradoSerializer,
)

from aplicaciones.usuarios.utils import registrar_bitacora
from aplicaciones.usuarios.usuario_views import get_client_ip 
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from aplicaciones.usuarios.permissions import IsAdminOrSuperAdmin
from django.views.decorators.csrf import csrf_exempt
from aplicaciones.usuarios.authentication import CsrfExemptSessionAuthentication
from rest_framework.permissions import IsAuthenticated
from aplicaciones.usuarios.authentication import MultiTokenAuthentication



class GradoViewSet(viewsets.ModelViewSet):
    queryset = Grado.objects.all()
    serializer_class = GradoSerializer
    filterset_fields = ['unidad_educativa', 'nivel_educativo']
    permission_classes = [IsAdminOrSuperAdmin]
    authentication_classes = [MultiTokenAuthentication]

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

    @csrf_exempt
    @action(detail=False, methods=['post'], url_path='crear')
    def crear_grado(self, request):
        serializer = CreateGradoSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            grado = serializer.save()
            # Serializar con serializer de lectura para obtener id y campos anidados
            read_serializer = GradoSerializer(grado, context={'request': request})
            print("Id Grado Creado: ", read_serializer.data['id'])

            registrar_bitacora(
                usuario=request.user,
                ip=get_client_ip(request),
                tabla_afectada='grado',
                accion='crear',
                descripcion='Creó un grado'
            )

            return Response(read_serializer.data, status=status.HTTP_201_CREATED)
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
            registrar_bitacora(
                usuario=request.user,
                ip=get_client_ip(request),
                tabla_afectada='grado',
                accion='editar',
                descripcion=f'Editó el grado {pk}'
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'], url_path='eliminar')
    def eliminar_grado(self, request, pk=None):
        try:
            grado = Grado.objects.get(pk=pk)
        except Grado.DoesNotExist:
            return Response({'detail': 'Grado no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        grado.delete()
        registrar_bitacora(
            usuario=request.user,
            ip=get_client_ip(request),
            tabla_afectada='grado',
            accion='eliminar',
            descripcion=f'Eliminó el grado {pk}'
        )

        return Response({'detail': 'Grado eliminado correctamente.'}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='listar')
    def listar_grados(self, request):
        grados = self.filter_queryset(self.get_queryset())
        serializer = GradoSerializer(grados, many=True)
        return Response(serializer.data)


class ParaleloViewSet(viewsets.ModelViewSet):
    queryset = Paralelo.objects.all()
    serializer_class = ParaleloSerializer
    permission_classes = [IsAdminOrSuperAdmin]
    authentication_classes = [MultiTokenAuthentication]
    filterset_fields = ['grado', 'letra']

    @action(detail=False, methods=['get'], url_path='listar')
    def listar_paralelos(self, request):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='cantidad')
    def cantidad_paralelos(self, request):
        count = self.get_queryset().count()
        return Response({'cantidad': count})
    
    @csrf_exempt
    @action(detail=False, methods=['post'], url_path='crear')
    def crear_paralelo(self, request):
        print("Creando paralelo")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        paralelo = serializer.save()

        # Crear curso automáticamente
        numero = paralelo.grado.numero
        letra = paralelo.letra
        nivel = paralelo.grado.get_nivel_educativo_display()
        sufijos = {1: 'ro', 2: 'do', 3: 'ro', 4: 'to', 5: 'to', 6: 'to'}
        suf = sufijos.get(numero, '°')
        nombre_curso = f"{numero}{suf} {letra} de {nivel}"

        # Crear curso vinculado al paralelo
        Curso.objects.create(paralelo=paralelo, nombre=nombre_curso)

        return Response(self.get_serializer(paralelo).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['put'], url_path='editar')
    def editar_paralelo(self, request, pk=None):
        paralelo = self.get_object()
        serializer = self.get_serializer(paralelo, data=request.data)
        serializer.is_valid(raise_exception=True)
        paralelo = serializer.save()
        return Response(self.get_serializer(paralelo).data)

    @action(detail=True, methods=['delete'], url_path='eliminar')
    def eliminar_paralelo(self, request, pk=None):
        paralelo = self.get_object()
        paralelo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CursoViewSet(viewsets.ModelViewSet):
    queryset = Curso.objects.all()
    serializer_class = CursoSerializer
    permission_classes = [IsAdminOrSuperAdmin]
    authentication_classes = [MultiTokenAuthentication]
    filterset_fields = ['paralelo']

    @action(detail=False, methods=['get'], url_path='listar')
    def listar_cursos(self, request):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)
    
    
    @action(detail=False, methods=['get'], url_path='listar-unidad-educativa')
    def listar_cursos_unidad_educativa(self, request):
        unidad_educativa_id = request.query_params.get('unidad_educativa_id')
        if unidad_educativa_id:
            cursos = self.get_queryset().filter(paralelo__grado__unidad_educativa_id=unidad_educativa_id)
        else:
            cursos = self.get_queryset()
        
        serializer = self.get_serializer(cursos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='cantidad')
    def cantidad_cursos(self, request):
        count = self.get_queryset().count()
        return Response({'cantidad': count})
    
    @csrf_exempt
    @action(detail=False, methods=['post'], url_path='crear')
    def crear_curso(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        curso = serializer.save()
        return Response(self.get_serializer(curso).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['put'], url_path='editar')
    def editar_curso(self, request, pk=None):
        curso = self.get_object()
        serializer = self.get_serializer(curso, data=request.data)
        serializer.is_valid(raise_exception=True)
        curso = serializer.save()
        return Response(self.get_serializer(curso).data)

    @action(detail=True, methods=['delete'], url_path='eliminar')
    def eliminar_curso(self, request, pk=None):
        curso = self.get_object()
        curso.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MateriaViewSet(viewsets.ModelViewSet):
    queryset = Materia.objects.all()
    serializer_class = MateriaSerializer
    permission_classes = [IsAdminOrSuperAdmin]
    authentication_classes = [MultiTokenAuthentication]
    filterset_fields = ['nombre']
    search_fields = ['nombre']

    @action(detail=False, methods=['get'], url_path='listar-materias')
    def listar_materias(self, request):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='cantidad-materias')
    def cantidad_materias(self, request):
        count = self.get_queryset().count()
        return Response({'cantidad': count})

    @csrf_exempt
    @action(detail=False, methods=['post'], url_path='crear-materia')
    def crear_materia(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        materia = serializer.save()
        return Response(self.get_serializer(materia).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['put'], url_path='editar-materia')
    def editar_materia(self, request, pk=None):
        materia = self.get_object()
        serializer = self.get_serializer(materia, data=request.data)
        serializer.is_valid(raise_exception=True)
        materia = serializer.save()
        return Response(self.get_serializer(materia).data)

    @action(detail=True, methods=['delete'], url_path='eliminar-materia')
    def eliminar_materia(self, request, pk=None):
        materia = self.get_object()
        materia.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MateriaCursoViewSet(viewsets.ModelViewSet):
    queryset = MateriaCurso.objects.all()
    serializer_class = MateriaCursoSerializer
    permission_classes = [IsAdminOrSuperAdmin]
    filterset_fields = ['curso', 'materia']

    @action(detail=False, methods=['get'], url_path='listar-asignaciones')
    def listar_asignaciones(self, request):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='cantidad-asignaciones')
    def cantidad_asignaciones(self, request):
        count = self.get_queryset().count()
        return Response({'cantidad': count})

    @action(detail=False, methods=['post'], url_path='crear-asignacion')
    def crear_asignacion(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        asignacion = serializer.save()
        return Response(self.get_serializer(asignacion).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['put'], url_path='editar-asignacion')
    def editar_asignacion(self, request, pk=None):
        asignacion = self.get_object()
        serializer = self.get_serializer(asignacion, data=request.data)
        serializer.is_valid(raise_exception=True)
        asignacion = serializer.save()
        return Response(self.get_serializer(asignacion).data)

    @action(detail=True, methods=['delete'], url_path='eliminar-asignacion')
    def eliminar_asignacion(self, request, pk=None):
        asignacion = self.get_object()
        asignacion.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
