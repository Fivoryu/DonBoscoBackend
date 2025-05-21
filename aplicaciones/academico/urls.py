from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'grados', views.GradoViewSet)
router.register(r'paralelos', views.ParaleloViewSet)
router.register(r'cursos', views.CursoViewSet)
router.register(r'materias', views.MateriaViewSet)
router.register(r'materias-curso', views.MateriaCursoViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('listar-grados/', views.GradoViewSet.as_view({'get': 'listar_grados'}), name='listar-grados'),
    path('crear-grado/', views.GradoViewSet.as_view({'post': 'crear_grado'}), name='crear-grado'),
    path('editar-grado/<int:pk>/', views.GradoViewSet.as_view({'put': 'editar_grado'}), name='editar-grado'),
    path('eliminar-grado/<int:pk>/', views.GradoViewSet.as_view({'delete': 'eliminar_grado'}), name='eliminar-grado'),
]
