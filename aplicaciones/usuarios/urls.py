from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .usuario_views import (
    UsuarioViewSet,
    RolViewSet,
    NotificacionViewSet,
    BitacoraViewSet,
    
)

router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet, basename='usuario')
router.register(r'roles', RolViewSet, basename='rol')
router.register(r'notificaciones', NotificacionViewSet, basename='notificacion')
router.register(r'bitacoras', BitacoraViewSet, basename='bitacora')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include([
        path('login/', UsuarioViewSet.as_view({'post': 'login'}), name='login'),
        path('logout/', UsuarioViewSet.as_view({'post': 'logout'}), name='logout'),
        path('register/', UsuarioViewSet.as_view({'post': 'register'}), name='register'),
        path('cantidad/', UsuarioViewSet.as_view({'get': 'cantidad'}), name='cantidad-usuarios'),
        path('perfil/', UsuarioViewSet.as_view({'get': 'perfil'}), name='perfil'),
        
        path('eliminar-usuario/<int:pk>/', UsuarioViewSet.as_view({'delete': 'eliminar_usuario'}), name='borrar-usuario'),
        path('editar-usuario/<int:pk>/', UsuarioViewSet.as_view({'put': 'editar_usuario'}), name='editar-usuario'),
        path('listar-usuarios/', UsuarioViewSet.as_view({'get': 'listar_usuarios'}), name='listar-usuarios'),
        path('listar-admins/', UsuarioViewSet.as_view({'get': 'listar_admins'}), name='listar-admins'),
        path('listar-superadmins/', UsuarioViewSet.as_view({'get': 'listar_superadmins'}), name='listar-superadmins'),
        path('cantidad-por-rol/', UsuarioViewSet.as_view({'get': 'cantidad_por_rol'}), name='cantidad-por-rol'),
    ])),
]