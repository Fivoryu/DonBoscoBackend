from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.db.models import OuterRef, Subquery, Q
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Colegio, Modulo, Aula, UnidadEducativa,SuperAdmin
from aplicaciones.usuarios.utils import registrar_bitacora
from aplicaciones.usuarios.usuario_views import get_client_ip 
from .serializers import (
    ColegioSerializer,
    ModuloSerializer,
    AulaSerializer,
    UnidadEducativaSerializer,
    CreateColegioSerializer,
    CreateModuloSerializer,
    CreateAulaSerializer,
    CreateUnidadEducativaSerializer
)
from aplicaciones.usuarios.authentication import CsrfExemptSessionAuthentication
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count

from aplicaciones.usuarios.permissions import IsSuperAdmin, IsAdminOrSuperAdmin
from aplicaciones.usuarios.authentication import MultiTokenAuthentication

class ColegioViewSet(viewsets.ModelViewSet):
    queryset = Colegio.objects.all()
    search_fields = ['nombre', 'direccion']
    permission_classes = [IsSuperAdmin]  # Permitir solo a SuperAdmin
    authentication_classes = [MultiTokenAuthentication]
    parser_classes = [MultiPartParser, FormParser]  # To handle file uploads

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CreateColegioSerializer
        return ColegioSerializer

    @action(detail=False, methods=['get'], url_path='cantidad')
    def obtener_cantidad_colegios(self, request):
        cantidad = Colegio.objects.count()
        registrar_bitacora(
            usuario=request.user,
            ip=get_client_ip(request),
            tabla_afectada='colegio',
            accion='ver',
            descripcion='Consultó la cantidad de colegios'
        )
        return Response({'cantidad_colegios': cantidad})

    @csrf_exempt
    @action(detail=False, methods=['post'], url_path='crear')
    def crear_colegio(self, request):
        """
        Endpoint to create a Colegio with the specified fields.
       """
        data = request.data.copy()

        usuario_id = data.get('usuario_id')
        if usuario_id:
            superadmin = SuperAdmin.objects.filter(usuario_id=usuario_id).first()
            if not superadmin:
                return Response({'error': 'SuperAdmin no encontrado'}, status=status.HTTP_400_BAD_REQUEST)
            data['super_admin_fk'] = superadmin.usuario_id
            data.pop('usuario_id', None)  # eliminar si no lo necesitas más

        serializer = CreateColegioSerializer(data=data, context={"request": request})
        print("serializer", serializer.initial_data)
        if serializer.is_valid():
            serializer.save()
            registrar_bitacora(
                usuario=request.user,
                ip=get_client_ip(request),
                tabla_afectada='colegio',
                accion='crear',
                descripcion=f'Creó el colegio nuevo'
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @csrf_exempt
    @action(detail=True, methods=['delete'], url_path='eliminar')
    def eliminar_colegio(self, request, pk=None):
        """
        Endpoint to delete a Colegio by its ID.
        """
        try:
            colegio = Colegio.objects.get(pk=pk)
            colegio.delete()
            registrar_bitacora(
                usuario=request.user,
                ip=get_client_ip(request),
                tabla_afectada='colegio',
                accion='eliminar',
                descripcion=f'Eliminó el colegio )'
            )
            return Response({'detail': 'Colegio eliminado exitosamente.'}, status=status.HTTP_204_NO_CONTENT)
        except Colegio.DoesNotExist:
            return Response({'detail': 'Colegio no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    @csrf_exempt
    @action(detail=True, methods=['put'], url_path='editar')
    def editar_colegio(self, request, pk=None):
        """
        Endpoint to edit a Colegio by its ID.
        """
        try:
            colegio = Colegio.objects.get(pk=pk)
            serializer = CreateColegioSerializer(colegio, data=request.data, partial=False)
            if serializer.is_valid():
                serializer.save()
                registrar_bitacora(
                    usuario=request.user,
                    ip=get_client_ip(request),
                    tabla_afectada='colegio',
                    accion='editar',
                    descripcion=f'Editó el colegio '
                )
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Colegio.DoesNotExist:
            return Response({'detail': 'Colegio no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'], url_path='listar')
    def listar_colegios(self, request):
        """
        Endpoint to list all Colegios.
        """
        colegios = Colegio.objects.all()
        serializer = ColegioSerializer(colegios, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='listar-colegios-unidades-educativas')
    def listar_colegios_unidades_educativas(self, request):
        data = Colegio.objects.filter(
            unidades_educativas__isnull=False  # Solo colegios con unidades educativas asociadas
        ).values('nombre', 'unidades_educativas__id')  # Obtener el nombre del colegio y el ID de la unidad educativa
        registrar_bitacora(
            usuario=request.user,
            ip=get_client_ip(request),
            tabla_afectada='colegio',
            accion='ver',
            descripcion='Listó colegios con unidades educativas asociadas'
        )
        return Response(data, status=status.HTTP_200_OK)

class ModuloViewSet(viewsets.ModelViewSet):
    queryset = Modulo.objects.annotate(cantidad_aulas_real=Count('aulas'))
    search_fields = ['nombre']
    filterset_fields = ['cantidad_aulas_real']
    permission_classes = [IsAuthenticated]
    authentication_classes = [MultiTokenAuthentication]

    def get_queryset(self):
        return Modulo.objects.annotate(
            aulas_ocupadas=Count('aulas', filter=Q(aulas__estado=True), distinct=True),
        )
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update',
                       'crear_modulo', 'editar_modulo']:
            return CreateModuloSerializer
        return ModuloSerializer

    @action(detail=False, methods=['get'], url_path='listar')
    def listar_modulos(self, request):
        modulos = self.get_queryset()
        serializer = self.get_serializer(modulos, many=True)
        
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['post'],
        url_path='crear',
        serializer_class=CreateModuloSerializer
    )
    def crear_modulo(self, request):
        # 1) Validación y guardado con el CreateModuloSerializer
        crear_ser = self.get_serializer(data=request.data)
        crear_ser.is_valid(raise_exception=True)
        modulo = crear_ser.save()

        # 2) Registrar bitácora
        registrar_bitacora(
            usuario=request.user,
            ip=get_client_ip(request),
            tabla_afectada='modulo',
            accion='crear',
            descripcion=f'Creó el módulo {modulo.nombre}'
        )

        # 3) Re-serializar con ModuloSerializer para devolver todos los campos
        read_ser = ModuloSerializer(modulo, context={'request': request})
        return Response(read_ser.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=['put'],
        url_path='editar',
        serializer_class=CreateModuloSerializer
    )
    def editar_modulo(self, request, pk=None):
        # 1) Recuperar instancia y validación
        modulo = self.get_object()
        editar_ser = self.get_serializer(modulo, data=request.data)
        editar_ser.is_valid(raise_exception=True)
        modulo = editar_ser.save()

        # 2) Registrar bitácora
        registrar_bitacora(
            usuario=request.user,
            ip=get_client_ip(request),
            tabla_afectada='modulo',
            accion='editar',
            descripcion=f'Editó el módulo {modulo.nombre}'
        )

        # 3) Re-serializar con ModuloSerializer
        read_ser = ModuloSerializer(modulo, context={'request': request})
        return Response(read_ser.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['delete'])
    def eliminar_modulo(self, request, pk=None):
        try:
            modulo = Modulo.objects.get(pk=pk)
        except Modulo.DoesNotExist:
            return Response({"detail": "No encontrado"}, status=status.HTTP_404_NOT_FOUND)
        modulo.delete()
        registrar_bitacora(
                usuario=request.user,
                ip=get_client_ip(request),
                tabla_afectada='modulo',
                accion='eliminar',
                descripcion=f'Eliminó el módulo )'
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

class AulaViewSet(viewsets.ModelViewSet):
    queryset = Aula.objects.all()
    filterset_fields = ['modulo', 'tipo', 'estado']
    search_fields = ['nombre', 'equipamiento']
    permission_classes = [IsAdminOrSuperAdmin]
    authentication_classes = [MultiTokenAuthentication]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update', 'crear_aula', 'editar_aula']:
            return CreateAulaSerializer
        return AulaSerializer

    @action(detail=False, methods=['get'], url_path='listar')
    def listar_aulas(self, request):
        aulas = Aula.objects.all()
        serializer = AulaSerializer(aulas, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['post'],
        url_path='crear',
        serializer_class=CreateAulaSerializer
    )
    def crear_aula(self, request):
        # 1) Validamos/creamos con el serializer de escritura
        crear_ser = self.get_serializer(data=request.data)
        crear_ser.is_valid(raise_exception=True)
        aula = crear_ser.save()

        # 2) Bitácora
        registrar_bitacora(
            usuario=request.user,
            ip=get_client_ip(request),
            tabla_afectada='aula',
            accion='crear',
            descripcion=f'Creó el aula {aula.nombre}'
        )

        # 3) Re-serializamos con el serializer de lectura para devolver nested módulo→colegio
        read_ser = AulaSerializer(aula, context={'request': request})
        return Response(read_ser.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=['put'],
        url_path='editar',
        serializer_class=CreateAulaSerializer
    )
    def editar_aula(self, request, pk=None):
        # 1) Recuperamos la instancia
        aula = self.get_object()

        # 2) Validamos/actualizamos con el serializer de escritura
        editar_ser = self.get_serializer(aula, data=request.data)
        editar_ser.is_valid(raise_exception=True)
        aula = editar_ser.save()

        # 3) Bitácora
        registrar_bitacora(
            usuario=request.user,
            ip=get_client_ip(request),
            tabla_afectada='aula',
            accion='editar',
            descripcion=f'Editó el aula {aula.nombre}'
        )

        # 4) Re-serializamos con el serializer de lectura
        read_ser = AulaSerializer(aula, context={'request': request})
        return Response(read_ser.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['delete'], url_path='eliminar')
    def eliminar_aula(self, request, pk=None):
        try:
            aula = Aula.objects.get(pk=pk)
        except Aula.DoesNotExist:
            registrar_bitacora(
                usuario=request.user,
                ip=get_client_ip(request),
                tabla_afectada='aula',
                accion='eliminar',
                descripcion=f'Eliminó el aula '
            )
            return Response({'detail': 'Aula no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        
        aula.delete()
        return Response({'detail': 'Aula eliminada'}, status=status.HTTP_204_NO_CONTENT)

class UnidadEducativaViewSet(viewsets.ModelViewSet):
    queryset = UnidadEducativa.objects.all()
    filterset_fields = ['colegio', 'turno']
    search_fields = ['codigo_sie', 'direccion']
    permission_classes = [IsAuthenticated]
    authentication_classes = [MultiTokenAuthentication]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CreateUnidadEducativaSerializer
        return UnidadEducativaSerializer

    @action(detail=False, methods=['get'], url_path='cantidad')
    def obtener_cantidad_unidades_educativas(self, request):
        cantidad = UnidadEducativa.objects.count()
        registrar_bitacora(
            usuario=request.user,
            ip=get_client_ip(request),
            tabla_afectada='unidad_educativa',
            accion='ver',
            descripcion='Consultó la cantidad de unidades educativas'
        )
        return Response({'cantidad_unidades_educativas': cantidad})
    
    @action(detail=False, methods=['post'], url_path='crear')
    def crear_unidad_educativa(self, request):
        serializer = CreateUnidadEducativaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            registrar_bitacora(
            usuario=request.user,
            ip=get_client_ip(request),
            tabla_afectada='unidad_educativa',
            accion='crear',
            descripcion='Creó una nueva unidad educativa'
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['put'], url_path='editar')
    def editar_unidad_educativa(self, request, pk=None):
        try:

            unidad = UnidadEducativa.objects.get(pk=pk)
        except UnidadEducativa.DoesNotExist:
            return Response({'detail': 'Unidad Educativa no encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CreateUnidadEducativaSerializer(unidad, data=request.data)
        print("serializer",serializer.initial_data)
        if serializer.is_valid():
            serializer.save()
            registrar_bitacora(
                usuario=request.user,
                ip=get_client_ip(request),
                tabla_afectada='unidad_educativa',
                accion='editar',
                descripcion=f'Editó la unidad educativa con ID: '
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['delete'], url_path='eliminar')
    def eliminar_unidad_educativa(self, request, pk=None):
        try:
            unidad = UnidadEducativa.objects.get(pk=pk)
            unidad.delete()
            registrar_bitacora(
                usuario=request.user,
                ip=get_client_ip(request),
                tabla_afectada='unidad_educativa',
                accion='eliminar',
                descripcion=f'Eliminó la unidad educativa con código SIE:'
            )
            return Response({'detail': 'Unidad Educativa eliminada exitosamente.'}, status=status.HTTP_204_NO_CONTENT)
        except UnidadEducativa.DoesNotExist:
            return Response({'detail': 'Unidad Educativa no encontrada.'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'], url_path='listar')
    def listar_unidades_educativas(self, request):
        unidades = UnidadEducativa.objects.all()
        serializer = UnidadEducativaSerializer(unidades, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

