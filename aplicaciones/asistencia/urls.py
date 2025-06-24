from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ComportamientoViewSet,
    LicenciaViewSet,
    AsistenciaGeneralViewSet,
    AsistenciaClaseViewSet
)

router = DefaultRouter()
router.register(r'comportamientos', ComportamientoViewSet, basename='comportamiento')
router.register(r'licencias', LicenciaViewSet, basename='licencia')
router.register(r'asistencias-generales', AsistenciaGeneralViewSet, basename='asistenciageneral')
router.register(r'asistencias-clases', AsistenciaClaseViewSet, basename='asistenciaclase')

urlpatterns = [
    path('', include(router.urls)),
]