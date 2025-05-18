from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ColegioViewSet, ModuloViewSet, AulaViewSet, UnidadEducativaViewSet
from . import views

router = DefaultRouter()
router.register(r'colegios', views.ColegioViewSet)
router.register(r'modulos', views.ModuloViewSet)
router.register(r'aulas', views.AulaViewSet)
router.register(r'unidades-educativas', views.UnidadEducativaViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

"""
urlpatterns = [
    path('', include(router.urls)),
    path('cantidad-colegios/', ColegioViewSet.as_view({'get': 'obtener_cantidad_colegios'}), name='cantidad-colegios'),
    path('cantidad-unidades-educativas/', UnidadEducativaViewSet.as_view({'get': 'obtener_cantidad_unidades_educativas'}), name='cantidad-unidades-educativas'),
    path('editar-colegio/<int:pk>/', ColegioViewSet.as_view({'put': 'editar_colegio'}), name='editar-colegio'),
    path('eliminar-colegio/<int:pk>/', ColegioViewSet.as_view({'delete': 'eliminar_colegio'}), name='eliminar-colegio'),
    path('nuevo-colegio/', ColegioViewSet.as_view({'post': 'crear_colegio'}), name='nuevo-colegio'),
    path('listar-colegios/', ColegioViewSet.as_view({'get': 'listar_colegios'}), name='listar-colegios'),
    path('nueva-unidad-educativa/', UnidadEducativaViewSet.as_view({'post': 'crear_unidad_educativa'}), name='nueva-unidad-educativa'),
    path('editar-unidad-educativa/<int:pk>/', UnidadEducativaViewSet.as_view({'put': 'editar_unidad_educativa'}), name='editar-unidad-educativa'),
    path('eliminar-unidad-educativa/<int:pk>/', UnidadEducativaViewSet.as_view({'delete': 'eliminar_unidad_educativa'}), name='eliminar-unidad-educativa'),
    path('listar-unidades-educativas/', UnidadEducativaViewSet.as_view({'get': 'listar_unidades_educativas'}), name='listar-unidades-educativas'),
    path('listar-colegios-unidades-educativas/', ColegioViewSet.as_view({'get': 'listar_colegios_unidades_educativas'}), name='listar-colegios-unidades-educativas'),    
    path('listar-modulos/', ModuloViewSet.as_view({'get': 'listar_modulos'}), name='listar-modulos'),
    path('nuevo-modulo/', ModuloViewSet.as_view({'post': 'crear_modulo'}), name='nuevo-modulo'),
    path('editar-modulo/<int:pk>/', ModuloViewSet.as_view({'put': 'editar_modulo'}), name='editar-modulo'),
    path('eliminar-modulo/<int:pk>/', ModuloViewSet.as_view({'delete': 'eliminar_modulo'}), name='eliminar-modulo'),
    path('listar-aulas/', AulaViewSet.as_view({'get': 'listar_aulas'}), name='listar-aulas'),
    path('nuevo-aula/', AulaViewSet.as_view({'post': 'crear_aula'}), name='nuevo-aula'),
    path('editar-aula/<int:pk>/', AulaViewSet.as_view({'put': 'editar_aula'}), name='editar-aula'),
    path('eliminar-aula/<int:pk>/', AulaViewSet.as_view({'delete': 'eliminar_aula'}), name='eliminar-aula'),
]

"""