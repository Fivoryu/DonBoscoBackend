from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import (
  CalendarioAcademico, Periodo, TipoFeriado, Feriado,
  TipoHorario, Horario, ClaseHorario
)

from .serializers import (
  CalendarioAcademicoSerializer, PeriodoSerializer,
  TipoFeriadoSerializer, FeriadoSerializer,
  TipoHorarioSerializer, HorarioSerializer, ClaseHorarioSerializer
)

from aplicaciones.usuarios.permissions import IsAdminOrSuperAdmin
from aplicaciones.usuarios.authentication import MultiTokenAuthentication
from aplicaciones.usuarios.utils import registrar_bitacora
from aplicaciones.usuarios.usuario_views import get_client_ip

class CalendarioAcademicoViewSet(viewsets.ModelViewSet):
    queryset = CalendarioAcademico.objects.all()
    serializer_class = CalendarioAcademicoSerializer
    permission_classes = [IsAdminOrSuperAdmin]
    authentication_classes = [MultiTokenAuthentication]

    @action(detail=False, methods=['get'], url_path='listar')
    def listar(self, request):
        qs = self.get_queryset()
        serializer = self.get_serializer(qs, many=True)
        registrar_bitacora(
            usuario=request.user,
            ip=get_client_ip(request),
            tabla_afectada='calendario_academico',
            accion='listar',
            descripcion='Listo el calendario academico'
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], url_path='crear')
    def crear(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            obj = serializer.save()
            registrar_bitacora(
                usuario=request.user,
                ip=get_client_ip(request),
                tabla_afectada='calendario_academico',
                accion='crear',
                descripcion=f'Creo el calendario academico {obj.año} - {obj.unidad_educativa.nombre}'
            )
            return Response(self.get_serializer(obj).data, status=status.HTTP_201_CREATED)
        return Response(serializer.erros, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['put'], url_path='editar')
    def editar(self, request, pk=None):
        obj = self.get_object()
        serializer = self.get_serializer(obj, data=request.data)
        if serializer.is_valid():
            obj = serializer.save()
            registrar_bitacora(
                usuario=request.user,
                ip=get_client_ip(request),
                tabla_afectada='calendario_academico',
                accion='editar',
                descripcion=f'Edito el calendario academico {obj.año} - {obj.unidad_educativa.nombre}'
            )
            return Response(self.get_serializer(obj).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'], url_path='eliminar')
    def eliminar(self, request, pk=None):
        obj = self.get_object()
        obj.delete()
        registar_bitacora(
            usuario=request.user,
            ip=get_client_ip(request),
            tabla_afectada='calendario_academico',
            accion='eliminar',
            descripcion=f'Elimino el calendario academico {obj.año} - {obj.unidad_educativa.nombre}'
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class PeriodoViewSet(viewsets.ModelViewSet):
    queryset = Periodo.objects.all()
    serializer_class = PeriodoSerializer
    permission_classes = [IsAdminOrSuperAdmin]
    authentication_classes = [MultiTokenAuthentication]

    @action(detail=False, methods=['get'], url_path='listar')
    def listar(self, request):
        qs = self.get_queryset()
        serializer = self.get_serializer(qs, many=True)
        registrar_bitacora(
            usuario=request.user,
            ip=get_client_ip(request),
            tabla_afectada='periodo',
            accion='listar',
            descripcion='Listo los periodos del calendario academico'
        )
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='crear')
    def crear(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            obj = serializer.save()
            registrar_bitacora(
                usuario=request.user,
                ip=get_client_ip(request),
                tabla_afectada='periodo',
                accion='crear',
                descripcion=f'Creo el periodo {obj.nombre} - {obj.calendario.año}'
            )
            return Response(self.get_serializer(obj).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['put'], url_path='editar')
    def editar(self, request, pk=None):
        obj = self.get_object()
        serializer = self.get_serializer(obj, data=request.data)
        if serializer.is_valid():
            obj = serializer.save()
            registrar_bitacora(
                usuario=request.user,
                ip=get_client_ip(request),
                tabla_afectada='periodo',
                accion='editar',
                descripcion=f'Edito el periodo {obj.nombre} - {obj.calendario.año}'
            )
            return Response(self.get_serializer(obj).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'], url_path='eliminar')
    def eliminar(self, request, pk=None):
        obj = self.get_object()
        obj.delete()
        registrar_bitacora(
                usuario=request.user,
                ip=get_client_ip(request),
                tabla_afectada='periodo',
                accion='eliminar',
                descripcion=f'Elimino el periodo {obj.nombre} - {obj.calendario.año}'
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

class TipoFeriadoViewSet(viewsets.ModelViewSet):
    queryset = TipoFeriado.objects.all()
    serializer_class = TipoFeriadoSerializer
    permission_classes = [IsAdminOrSuperAdmin]
    authentication_classes = [MultiTokenAuthentication]

    @action(detail=False, methods=['get'], url_path='listar')
    def listar(self, request):
        qs = self.get_queryset()
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='crear')
    def crear(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            obj = serializer.save()
            registrar_bitacora(
                usuario=request.user,
                ip=get_client_ip(request),
                tabla_afectada='tipo_feriado',
                descripcion=f'Creo el tipo de feriado {obj.nombre}'
            )
            return Response(self.get_serializer(obj).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['put'], url_path='editar')
    def editar(self, request, pk=None):
        obj = self.get_object()
        serializer = self.get_serializer(obj, data=request.data)
        if serializer.is_valid():
            obj = serializer.save()
            return Response(self.get_serializer(obj).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'], url_path='eliminar')
    def eliminar(self, request, pk=None):
        obj = self.get_object()
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FeriadoViewSet(viewsets.ModelViewSet):
    queryset = Feriado.objects.all()
    serializer_class = FeriadoSerializer
    permission_classes = [IsAdminOrSuperAdmin]
    authentication_classes = [MultiTokenAuthentication]

    @action(detail=False, methods=['get'], url_path='listar')
    def listar(self, request):
        qs = self.get_queryset()
        serializer = self.get_serializer(qs, many=True)
        registrar_bitacora(
            usuario=request.user,
            ip=get_client_ip(request),
            tabla_afectada='feriado',
            accion='listar',
            descripcion='Listo los feriados del calendario academico'
        )
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='crear')
    def crear(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            obj = serializer.save()
            registrar_bitacora(
                usuario=request.user,
                ip=get_client_ip(request),
                tabla_afectada='feriado',
                accion='crear',
                descripcion=f'Creo el feriado {obj.nombre} - {obj.fecha} en el calendario {obj.calendario.año}'
            )
            return Response(self.get_serializer(obj).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['put'], url_path='editar')
    def editar(self, request, pk=None):
        obj = self.get_object()
        serializer = self.get_serializer(obj, data=request.data)
        if serializer.is_valid():
            obj = serializer.save()
            registrar_bitacora(
                usuario=request.user,
                ip=get_client_ip(request),
                tabla_afectada='feriado',
                accion='editar',
                descripcion=f'Edito el feriado {obj.nombre} - {obj.fecha} en el calendario {obj.calendario.año}'
            )
            return Response(self.get_serializer(obj).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'], url_path='eliminar')
    def eliminar(self, request, pk=None):
        obj = self.get_object()
        obj.delete()
        registrar_bitacora(
            usuario=request.user,
            ip=get_client_ip(request),
            tabla_afectada='feriado',
            accion='eliminar',
            descripcion=f'Elimino el feriado {obj.nombre} - {obj.fecha} en el calendario {obj.calendario.año}'
        )
        return Response(status=status.HTTP_204_NO_CONTENT)

class TipoHorarioViewSet(viewsets.ModelViewSet):
    queryset = TipoHorario.objects.all()
    serializer_class = TipoHorarioSerializer
    permission_classes = [IsAdminOrSuperAdmin]
    authentication_classes = [MultiTokenAuthentication]

    @action(detail=False, methods=['get'], url_path='listar')
    def listar(self, request):
        qs = self.get_queryset()
        serializer = self.get_serializer(qs, many=True)
        registrar_bitacora(
            usuario=request.user,
            ip=get_client_ip(request),
            tabla_afectada='tipo_feriado',
            accion='listar',
            descripcion='Listo los tipos de horario disponibles'
        )
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='crear')
    def crear(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            obj = serializer.save()
            registrar_bitacora (
                usuario=request.user,
                ip=get_client_ip(request),
                tabla_afectada='tipo_horario',
                accion='crear',
                descripcion=f'Creo el tipo de horario {obj.nombre} {obj.turno}'
            )
            return Response(self.get_serializer(obj).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['put'], url_path='editar')
    def editar(self, request, pk=None):
        obj = self.get_object()
        serializer = self.get_serializer(obj, data=request.data)
        if serializer.is_valid():
            obj = serializer.save()
            registrar_bitacora (
                usuario=request.user,
                ip=get_client_ip(request),
                tabla_afectada='tipo_horario',
                accion='editar',
                descripcion=f'Edito el tipo de horario {obj.nombre} {obj.turno}'
            )
            return Response(self.get_serializer(obj).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'], url_path='eliminar')
    def eliminar(self, request, pk=None):
        obj = self.get_object()
        obj.delete()
        registrar_bitacora (
                usuario=request.user,
                ip=get_client_ip(request),
                tabla_afectada='tipo_horario',
                accion='eliminar',
                descripcion=f'Elimino el tipo de horario {obj.nombre} {obj.turno}'
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class HorarioViewSet(viewsets.ModelViewSet):
    queryset = Horario.objects.all()
    serializer_class = HorarioSerializer
    permission_classes = [IsAdminOrSuperAdmin]
    authentication_classes = [MultiTokenAuthentication]

    @action(detail=False, methods=['get'], url_path='listar')
    def listar(self, request):
        qs = self.get_queryset()
        serializer = self.get_serializer(qs, many=True)
        registrar_bitacora (
            usuario=request.user,
            ip=get_client_ip(request),
            tabla_afectada='horario',
            accion='listar',
            descripcion='Listo los horarios disponibles'
        )
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='crear')
    def crear(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            obj = serializer.save()
            registrar_bitacora (
                usuario=request.user,
                ip=get_client_ip(request),
                tabla_afectada='horario',
                accion='crear',
                descripcion=f'Creo el horario {obj.tipo.nombre} {obj.dia} {obj.hora_inicio} - {obj.hora_fin}'
            )
            return Response(self.get_serializer(obj).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['put'], url_path='editar')
    def editar(self, request, pk=None):
        obj = self.get_object()
        serializer = self.get_serializer(obj, data=request.data)
        if serializer.is_valid():
            obj = serializer.save()
            registrar_bitacora (
                usuario=request.user,
                ip=get_client_ip(request),
                tabla_afectada='horario',
                accion='editar',
                descripcion=f'Edito el horario {obj.tipo.nombre} {obj.dia_display} {obj.hora_inicio} - {obj.hora_fin}'
            )
            return Response(self.get_serializer(obj).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'], url_path='eliminar')
    def eliminar(self, request, pk=None):
        obj = self.get_object()
        obj.delete()
        registrar_bitacora (
            usuario=request.user,
            ip=get_client_ip(request),
            tabla_afectada='horario',
            accion='eliminar',
            descripcion=f'Elimino el horario {obj.tipo.nombre} {obj.dia_display} {obj.hora_inicio} - {obj.hora_fin}'
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class ClaseHorarioViewSet(viewsets.ModelViewSet):
    queryset = ClaseHorario.objects.all()
    serializer_class = ClaseHorarioSerializer
    permission_classes = [IsAdminOrSuperAdmin]
    authentication_classes = [MultiTokenAuthentication]

    @action(detail=False, methods=['get'], url_path='listar')
    def listar(self, request):
        qs = self.get_queryset()
        serializer = self.get_serializer(qs, many=True)
        registar_bitacora(
            usuario=request.user,
            ip=get_client_ip(request),
            tabla_afectada='clase_horario',
            accion='listar',
            descripcion='Listo las clases de horario disponibles'
        )
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='crear')
    def crear(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            obj = serializer.save()
            registrar_bitacora(
                usuario=request.user,
                ip=get_client_ip(request),
                tabla_afectada='clase_horario',
                accion='crear',
                descripcion=f'Creo la clase de horario {obj.clase_id} - {obj.horario_id}'
            )
            return Response(self.get_serializer(obj).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['put'], url_path='editar')
    def editar(self, request, pk=None):
        obj = self.get_object()
        serializer = self.get_serializer(obj, data=request.data)
        if serializer.is_valid():
            obj = serializer.save()
            registrar_bitacora(
                usuario=request.user,
                ip=get_client_ip(request),
                tabla_afectada='clase_horario',
                accion='editar',
                descripcion=f'Edito la clase de horario {obj.clase_id} - {obj.horario_id}'
            )
            return Response(self.get_serializer(obj).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'], url_path='eliminar')
    def eliminar(self, request, pk=None):
        obj = self.get_object()
        obj.delete()
        registrar_bitacora(
            usuario=request.user,
            ip=get_client_ip(request),
            tabla_afectada='clase_horario',
            accion='crear',
            descripcion=f'Edito la clase de horario {obj.clase_id} - {obj.horario_id}'
        )
        return Response(status=status.HTTP_204_NO_CONTENT)

        