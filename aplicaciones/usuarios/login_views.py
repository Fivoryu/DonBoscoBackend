from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from aplicaciones.usuarios.models import Usuario
from django.contrib.auth import authenticate
from . import serializer

from usuarios.models import Bitacora

@api_view(['GET'])
def home_api(request):
    content = HomeContent.objects.first()
    if not content:
        content = HomeContent.objects.create(
            welcome_message="Bienvenidos al Colegio Don Bosco",
            features=[
                {"title": "Excelencia Académica", "description": "..."},
                # ... más features
            ],
            testimonials=[
                {"author": "Padre de Familia", "text": "..."},
                # ... más testimonios
            ]
        )
    serializer = HomeContentSerializer(content)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    try:
        username = request.data.get("username")
        password = request.data.get("password")
        print(username)
        print(password)
        
        if not username or not password:
            return Response({"error": "Credenciales requeridas"}, status=400)

        user = authenticate(request, username=username, password=password)
        
        if not user:
            # Verifica si el usuario existe pero la contraseña está mal
            user_exists = Usuario.objects.filter(username=username).exists()
            return Response({
                "error": "Credenciales inválidas",
                "user_exists": user_exists
            }, status=401)
            
        token, _ = Token.objects.get_or_create(user=user)
        
        return Response({
            "token": token.key,
            "user": {
                "id": user.id,
                "username": user.username,
                "rol": user.rol.nombre if user.rol else None
            }
        })
        
    except Exception as e:
        return Response({"error": str(e)}, status=500)