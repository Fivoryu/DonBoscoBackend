from django.urls import path, include
from django.views.generic import TemplateView
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),  # Para la autenticación de DRF
    path("user/", include("aplicaciones.usuarios.urls")),  
    path('institucion/', include("aplicaciones.institucion.urls")),
    path('', TemplateView.as_view(template_name='index.html')),  # Para servir React
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
