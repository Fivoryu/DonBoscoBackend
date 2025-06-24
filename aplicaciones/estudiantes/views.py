# aplicaciones/personal/views.py
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from aplicaciones.usuarios.permissions import IsTutor, PermisoEstudianteView, PermisoPorPuesto, PermisoPorRol
from aplicaciones.usuarios.utils import registrar_bitacora
from aplicaciones.usuarios.usuario_views import get_client_ip
from aplicaciones.usuarios.authentication import MultiTokenAuthentication
from .models import Estudiante, Tutor, TutorEstudiante
from rest_framework.permissions import IsAuthenticated
from .serializers import (
    EstudianteSerializer, CreateEstudianteSerializer,
    TutorSerializer, CreateTutorSerializer,
    TutorEstudianteSerializer, CreateTutorEstudianteSerializer
)
from aplicaciones.evaluacion.models import NotaFinalMateria, NotaActividad
from aplicaciones.evaluacion.serializers import (
    NotaFinalMateriaSerializer,
    NotaActividadSerializer,
)
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action

class EstudianteViewSet(viewsets.ModelViewSet):
    queryset = Estudiante.objects.select_related('usuario','curso').all()
    permission_classes = [PermisoPorPuesto, PermisoPorRol, PermisoEstudianteView]
    authentication_classes = [MultiTokenAuthentication]

    def get_queryset(self):
        user = self.request.user 
        qs = super().get_queryset()

        # SuperAdmin / Admin pueden ver todos los estudiantes
        if hasattr(user, 'superadmin') or hasattr(user, 'admin'):
            return qs
        
        # Tutor: solo ve sus propios estudiantes
        if hasattr(user, 'tutor'):
            return qs.filter(tutores__tutor__usuario=user).distinct()
        
        # Estudiante: solo ve su propio perfil
        if hasattr(user, 'estudiante'):
            return qs.filter(pk.user.pk)
        
        if hasattr(user, 'profesor'):
            prof = user.profesor
            return qs.filter(
                Q(curso__tutor_id=prof.tutor_id) |
                Q(curso__materias__profesor=prof)
            ).distinct()
        
        return Estudiante.objects.none()  # No acceso


    def get_serializer_class(self):
        if self.action in ['crear_estudiante','editar_estudiante']:
            return CreateEstudianteSerializer
        return EstudianteSerializer

    @action(detail=False, methods=['get'], url_path='listar')
    def listar(self, request):
        qs = self.get_queryset()
        serializer = EstudianteSerializer(qs, many=True)
        registrar_bitacora(request.user, get_client_ip(request), 'estudiante', 'ver', 'Listar estudiantes')
        return Response(serializer.data)

    
    @action(detail=True, methods=['get'], url_path='mi-estudiante', permission_classes=[IsTutor])
    def ver_mi_estudiante(self, request, pk=None):
      """
      Permite a un tutor ver el detalle de un estudiante solo si está vinculado a él.
      """
      user = request.user
      tutor = getattr(user, 'tutor', None)

      if not tutor:
        return Response({"detail": "No es un tutor válido"}, status=status.HTTP_403_FORBIDDEN)

      try:
          relacion = TutorEstudiante.objects.select_related("estudiante").get(tutor=tutor, estudiante_id=pk)
          estudiante = relacion.estudiante
          serializer = EstudianteSerializer(estudiante)
          return Response(serializer.data)
      except TutorEstudiante.DoesNotExist:
        return Response({"detail": "No tienes acceso a este estudiante"}, status=status.HTTP_403_FORBIDDEN)
    
    @csrf_exempt
    @action(detail=False, methods=['post'], url_path='crear')
    def crear_estudiante(self, request):
        data = request.data.copy()
        # Si el usuario debe crearse aquí, hazlo antes y asigna el id al estudiante
        usuario_data = data.pop('usuario', None)
        if usuario_data:
            from aplicaciones.usuarios.models import Usuario
            from aplicaciones.usuarios.serializer import UsuarioSerializer
            usuario_serializer = UsuarioSerializer(data=usuario_data)
            usuario_serializer.is_valid(raise_exception=True)
            usuario = usuario_serializer.save()
            data['usuario'] = usuario.id
        serializer = CreateEstudianteSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            est = serializer.save()
            registrar_bitacora(request.user, get_client_ip(request), 'estudiante', 'crear', f'Crear estudiante {est}')
        return Response(EstudianteSerializer(est).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['put'], url_path='editar')
    def editar_estudiante(self, request, pk=None):
        est = self.get_object()
        serializer = CreateEstudianteSerializer(est, data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            est = serializer.save()
            registrar_bitacora(request.user, get_client_ip(request), 'estudiante', 'editar', f'Editar estudiante {est}')
        return Response(EstudianteSerializer(est).data)
    
    @action(
    detail=True,
    methods=["get"],
    url_path="notas",
    permission_classes=[AllowAny]
    )
    def notas(self, request, pk=None):
        """
          Devuelve todas las notas (finales y de actividad) para el estudiante pk.
          Permite filtrar por año: ?anio=2025
         """
        anio = request.query_params.get('anio')

        notas_finales_qs = NotaFinalMateria.objects.filter(estudiante_id=pk)
        notas_actividades_qs = NotaActividad.objects.filter(estudiante_id=pk)

        if anio:
            notas_finales_qs = notas_finales_qs.filter(periodo__calendario__año=anio)

        notas_finales = NotaFinalMateriaSerializer(notas_finales_qs, many=True).data
        notas_actividades = NotaActividadSerializer(notas_actividades_qs, many=True).data

        return Response({
        'notas_finales': notas_finales,
        'notas_actividades': notas_actividades
    }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='curso/(?P<curso_id>[^/.]+)')
    def listar_por_curso(self, request, curso_id=None):
      estudiantes = self.get_queryset().filter(curso_id=curso_id)
      serializer = EstudianteSerializer(estudiantes, many=True)
      registrar_bitacora(request.user, get_client_ip(request), 'estudiante', 'ver', f'Estudiantes del curso {curso_id}')
      return Response(serializer.data)    

    @action(detail=True, methods=['delete'], url_path='eliminar')
    def eliminar_estudiante(self, request, pk=None):
        est = self.get_object()
        est.delete()
        registrar_bitacora(request.user, get_client_ip(request), 'estudiante', 'eliminar', f'Eliminar estudiante {pk}')
        return Response(status=status.HTTP_204_NO_CONTENT)


class TutorViewSet(viewsets.ModelViewSet):
    queryset = Tutor.objects.select_related('usuario').all()
    permission_classes = [PermisoPorPuesto]
    authentication_classes = [MultiTokenAuthentication]

    def get_serializer_class(self):
        if self.action in ['crear_tutor','editar_tutor']:
            return CreateTutorSerializer
        return TutorSerializer

    @action(detail=False, methods=['get'], url_path='listar')
    def listar(self, request):
        serializer = TutorSerializer(self.get_queryset(), many=True)
        registrar_bitacora(request.user, get_client_ip(request), 'tutor', 'ver', 'Listar tutores')
        return Response(serializer.data)

    @csrf_exempt
    @action(detail=False, methods=['post'], url_path='crear')
    def crear_tutor(self, request):
        serializer = CreateTutorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            t = serializer.save()
            registrar_bitacora(request.user, get_client_ip(request), 'tutor', 'crear', f'Crear tutor {t}')
        return Response(TutorSerializer(t).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['put'], url_path='editar')
    def editar_tutor(self, request, pk=None):
        t = self.get_object()
        serializer = CreateTutorSerializer(t, data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            t = serializer.save()
            registrar_bitacora(request.user, get_client_ip(request), 'tutor', 'editar', f'Editar tutor {t}')
        return Response(TutorSerializer(t).data)

    @action(detail=True, methods=['delete'], url_path='eliminar')
    def eliminar_tutor(self, request, pk=None):
        t = self.get_object()
        t.delete()
        registrar_bitacora(request.user, get_client_ip(request), 'tutor', 'eliminar', f'Eliminar tutor {pk}')
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=["get"], url_path="usuario/(?P<usuario_id>[^/.]+)")
    def get_by_usuario(self, request, usuario_id=None):
        try:
            tutor = Tutor.objects.get(usuario_id=usuario_id)
            serializer = self.get_serializer(tutor)
            return Response(serializer.data)
        except Tutor.DoesNotExist:
            return Response({"detail": "No existe"}, status=status.HTTP_404_NOT_FOUND)
    
        


class TutorEstudianteViewSet(viewsets.ModelViewSet):
    queryset = TutorEstudiante.objects.select_related('tutor__usuario','estudiante__usuario').all()
    permission_classes = [PermisoPorPuesto]
    authentication_classes = [MultiTokenAuthentication]

    def get_serializer_class(self):
        if self.action in ['crear_relacion','editar_relacion']:
            return CreateTutorEstudianteSerializer
        return TutorEstudianteSerializer

    @action(detail=False, methods=['get'], url_path='listar')
    def listar(self, request):
        data = TutorEstudianteSerializer(self.get_queryset(), many=True)
        registrar_bitacora(request.user, get_client_ip(request), 'tutor_estudiante', 'ver', 'Listar relaciones')
        return Response(data.data)

    @csrf_exempt
    @action(detail=False, methods=['post'], url_path='crear')
    def crear_relacion(self, request):
        serializer = CreateTutorEstudianteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            rel = serializer.save()
            registrar_bitacora(request.user, get_client_ip(request), 'tutor_estudiante', 'crear', f'Crear relación {rel}')
        return Response(TutorEstudianteSerializer(rel).data, status=status.HTTP_201_CREATED)
    
    from rest_framework.permissions import IsAuthenticated

    @action(detail=False, methods=['get'], url_path='mis-estudiantes', permission_classes=[IsTutor])
    def mis_estudiantes(self, request):
     print("Mis estudiantes")
     print(request.user)
     print(getattr(request.user, 'tutor', None))   
     tutor = getattr(request.user, 'tutor', None)
     if tutor is None:
        return Response({"detail": "No es un tutor válido"}, status=403)

     relaciones = self.get_queryset().filter(tutor=tutor)
     estudiantes = [rel.estudiante for rel in relaciones]
     from aplicaciones.estudiantes.serializers import EstudianteSerializer
     data = EstudianteSerializer(estudiantes, many=True).data
     return Response(data)


    @action(detail=True, methods=['put'], url_path='editar')
    def editar_relacion(self, request, pk=None):
        rel = self.get_object()
        serializer = CreateTutorEstudianteSerializer(rel, data=request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            rel = serializer.save()
            registrar_bitacora(request.user, get_client_ip(request), 'tutor_estudiante', 'editar', f'Editar relación {rel}')
        return Response(TutorEstudianteSerializer(rel).data)

    @action(detail=True, methods=['delete'], url_path='eliminar')
    def eliminar_relacion(self, request, pk=None):
        rel = self.get_object()
        rel.delete()
        registrar_bitacora(request.user, get_client_ip(request), 'tutor_estudiante', 'eliminar', f'Eliminar relación {pk}')
        return Response(status=status.HTTP_204_NO_CONTENT)
