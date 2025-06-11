from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import CargaHorariaViewSet

router = DefaultRouter()
router.register(r'profesores', views.ProfesorViewSet)
router.register(r'especialidades', views.EspecialidadViewSet)
router.register(r'asignaciones', views.ProfesorEspecialidadViewSet, basename='profesor-especialidad')
router.register(r'carga_horaria', CargaHorariaViewSet, basename='carga_horaria')

urlpatterns = [
    path('', include(router.urls)),
]