from django.forms import ValidationError
from rest_framework.viewsets import ModelViewSet 
from rest_framework import viewsets
from .models import Grado, Paralelo, Curso, Materia, MateriaCurso,Clase
from .serializers import (
    GradoSerializer,
    ParaleloSerializer,
    CursoSerializer,
    MateriaSerializer,
    MateriaCursoSerializer,
    CreateGradoSerializer,
    CreateMateriaCursoSerializer,
    ClaseSerializer
)

from aplicaciones.usuarios.utils import registrar_bitacora
from aplicaciones.usuarios.usuario_views import get_client_ip 
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from django.views.decorators.csrf import csrf_exempt
from aplicaciones.usuarios.authentication import CsrfExemptSessionAuthentication
from rest_framework.permissions import IsAuthenticated
from aplicaciones.usuarios.authentication import MultiTokenAuthentication
from aplicaciones.usuarios.permissions import IsAdminOrSuperAdmin, PermisoPorPuesto, PermisoPorRol



class GradoViewSet(viewsets.ModelViewSet):
    queryset = Grado.objects.all()
    serializer_class = GradoSerializer
    filterset_fields = ['unidad_educativa', 'nivel_educativo']
    permission_classes = [PermisoPorRol | PermisoPorPuesto]
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
    permission_classes = [PermisoPorRol | PermisoPorPuesto]
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

        registrar_bitacora(
            usuario=request.user,
            ip=get_client_ip(request),
            tabla_afectada='paralelo',
            descripcion=f'Actualizo el paralelo {paralelo.id} {paralelo.nobmre}'
        )

        # ——— Aquí actualizamos también el Curso vinculado ———
        try:
            curso = paralelo.curso  # dado el OneToOneField relacionado
        except Curso.DoesNotExist:
            # Si por algún motivo no existiera, lo creamos:
            curso = Curso(paralelo=paralelo)
        
        numero = paralelo.grado.numero
        letra = paralelo.letra
        nivel = paralelo.grado.get_nivel_educativo_display()
        sufijos = {1: 'ro', 2: 'do', 3: 'ro', 4: 'to', 5: 'to', 6: 'to'}
        suf = sufijos.get(numero, '°')
        nuevo_nombre = f"{numero}{suf} {letra} de {nivel}"

        curso.nombre = nuevo_nombre
        curso.save()
        registrar_bitacora(
            usuario=request.user,
            ip=get_client_ip(request),
            tabla_afectada='curso',
            descripcion=f'Actualizó el curso vinculado al paraeleo {paralelo.id} {paralelo.nombre}'
        )
        # ——————————————————————————————————————————

        return Response(self.get_serializer(paralelo).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['delete'], url_path='eliminar')
    def eliminar_paralelo(self, request, pk=None):
        paralelo = self.get_object()
        try:
            curso = paralelo.curso
            registrar_bitacora(
                usuario=request.user,
                ip=get_client_ip(request),
                tabla_afectada='curso',
                accion='eliminar',
                descripcion=f'Elimino el curso {curso.id} {curso.nombre} vinculado al paralelo {paralelo.id} {paralelo.nombre}',
            )
        except Curso.DoesNotExist:
            pass

        paralelo.delete()
        registrar_bitacora(
            usuario=request.user,
            ip=get_client_ip(request),
            tabla_afectada='paralelo',
            acion='eliminar',
            descripcion=f'Elimino el paralelo {paralelo.id} {paralelo.nombre}',
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class CursoViewSet(viewsets.ModelViewSet):
    queryset = Curso.objects.all()
    serializer_class = CursoSerializer
    permission_classes = [PermisoPorRol | PermisoPorPuesto]
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
    permission_classes = [PermisoPorRol | PermisoPorPuesto]
    authentication_classes = [MultiTokenAuthentication]
    filterset_fields = ['nombre']
    search_fields = ['nombre']

    @action(detail=False, methods=['get'], url_path='listar')
    def listar_materias(self, request):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='cantidad')
    def cantidad_materias(self, request):
        count = self.get_queryset().count()
        return Response({'cantidad': count})

    @csrf_exempt
    @action(detail=False, methods=['post'], url_path='crear')
    def crear_materia(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        materia = serializer.save()
        return Response(self.get_serializer(materia).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['put'], url_path='editar')
    def editar_materia(self, request, pk=None):
        materia = self.get_object()
        serializer = self.get_serializer(materia, data=request.data)
        serializer.is_valid(raise_exception=True)
        materia = serializer.save()
        return Response(self.get_serializer(materia).data)

    @action(detail=True, methods=['delete'], url_path='eliminar')
    def eliminar_materia(self, request, pk=None):
        materia = self.get_object()
        materia.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MateriaCursoViewSet(viewsets.ModelViewSet):
    queryset = MateriaCurso.objects.all()
    serializer_class = MateriaCursoSerializer
    permission_classes = [PermisoPorRol | PermisoPorPuesto]
    authentication_classes = [MultiTokenAuthentication]
    filterset_fields = ['curso', 'materia']

    def get_serializer_class(self):
        if self.action in ['crear_asignacion', 'editar_asignacion', 'list', 'retrieve']:
            return CreateMateriaCursoSerializer
        return MateriaCursoSerializer

    @action(detail=False, methods=['get'], url_path='listar-asignaciones')
    def listar_asignaciones(self, request):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='cantidad-asignaciones')
    def cantidad_asignaciones(self, request):
        count = self.get_queryset().count()
        return Response({'cantidad': count})

    @action(
        detail=False,
        methods=['post'],
        url_path='crear-asignacion',
        serializer_class=CreateMateriaCursoSerializer  # <— aquí
    )
    def crear_asignacion(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        asignacion = serializer.save()
        return Response(
            MateriaCursoSerializer(asignacion).data,  # o self.get_serializer(asignacion).data si ajustas get_serializer_class
            status=status.HTTP_201_CREATED
        )

    @action(
        detail=True,
        methods=['put'],
        url_path='editar-asignacion',
        serializer_class=CreateMateriaCursoSerializer
    )
    def editar_asignacion(self, request, pk=None):
        asign = self.get_object()
        serializer = self.get_serializer(asign, data=request.data)
        serializer.is_valid(raise_exception=True)
        asign = serializer.save()
        return Response(MateriaCursoSerializer(asign).data)

    @action(detail=True, methods=['delete'], url_path='eliminar-asignacion')
    def eliminar_asignacion(self, request, pk=None):
        asignacion = self.get_object()
        asignacion.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        url_path='listar-unidad-educativa'
    )
    def listar_por_unidad_educativa(self, request):
        """
        Parámetros:
          • unidad_educativa_id : int  (obligatorio para filtrar)

        Devuelve todas las asignaciones MateriaCurso cuyo curso pertenece
        a la unidad educativa indicada.
        """
        unidad_id = request.query_params.get('unidad_educativa_id')
        qs = self.filter_queryset(self.get_queryset())

        if unidad_id:
            qs = qs.filter(
                curso__paralelo__grado__unidad_educativa_id=unidad_id
            )
        else:
            # Si no llega el parámetro devolvemos lista vacía (o todas, según prefieras)
            return Response([], status=status.HTTP_200_OK)

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class ClaseViewSet(viewsets.ModelViewSet):
    
    queryset = Clase.objects.select_related(
        'materia_curso__materia', 'materia_curso__curso', 'aula'
    )
    serializer_class      = ClaseSerializer
    permission_classes = [PermisoPorRol | PermisoPorPuesto]
    authentication_classes = [MultiTokenAuthentication]
    filterset_fields      = ['materia_curso', 'aula']
    search_fields         = ['materia_curso__materia__nombre',
                             'materia_curso__curso__nombre',
                             'aula__nombre']

    # ---------- LISTAR ----------
    @action(detail=False, methods=['get'], url_path='listar')
    def listar_clases(self, request):
        serializer = self.get_serializer(self.filter_queryset(self.get_queryset()), many=True)
        return Response(serializer.data)

    # ---------- CANTIDAD ----------
    @action(detail=False, methods=['get'], url_path='cantidad')
    def cantidad_clases(self, request):
        return Response({'cantidad': self.get_queryset().count()})

    # ---------- CREAR ----------
    @csrf_exempt
    @action(detail=False, methods=['post'], url_path='crear')
    def crear_clase(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # evita duplicado materia_curso + aula
        mc   = serializer.validated_data['materia_curso']
        aula = serializer.validated_data['aula']
        if Clase.objects.filter(materia_curso=mc, aula=aula).exists():
            raise ValidationError('Esa materia/curso ya está asignada a ese aula.')

        clase = serializer.save()
        registrar_bitacora(
            usuario=request.user,
            ip=get_client_ip(request),
            tabla_afectada='clase',
            accion='crear',
            descripcion=f'Creó la clase {clase.id}'
        )
        return Response(self.get_serializer(clase).data, status=status.HTTP_201_CREATED)

    # ---------- EDITAR ----------
    @action(detail=True, methods=['put'], url_path='editar')
    def editar_clase(self, request, pk=None):
        clase = self.get_object()
        serializer = self.get_serializer(clase, data=request.data)
        serializer.is_valid(raise_exception=True)

        mc   = serializer.validated_data['materia_curso']
        aula = serializer.validated_data['aula']
        if Clase.objects.filter(materia_curso=mc, aula=aula).exclude(id=clase.id).exists():
            raise ValidationError('Otra clase con esa materia/curso y aula ya existe.')

        clase = serializer.save()
        registrar_bitacora(
            usuario=request.user,
            ip=get_client_ip(request),
            tabla_afectada='clase',
            accion='editar',
            descripcion=f'Editó la clase {clase.id}'
        )
        return Response(self.get_serializer(clase).data)

    # ---------- ELIMINAR ----------
    @action(detail=True, methods=['delete'], url_path='eliminar')
    def eliminar_clase(self, request, pk=None):
        clase = self.get_object()
        registrar_bitacora(
            usuario=request.user,
            ip=get_client_ip(request),
            tabla_afectada='clase',
            accion='eliminar',
            descripcion=f'Eliminó la clase {clase.id}'
        )
        clase.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
