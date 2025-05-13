from django.test import TestCase, Client
from django.urls import reverse
from .models import Usuario, Rol
import json

class LoginTests(TestCase):
    def setUp(self):
        rol = Rol.objects.create(nombre="Tester")
        self.user = Usuario.objects.create_user(
            ci="123",
            email="test@example.com",
            nombre="Test",
            apellido="User",
            username="tester",
            password="clave123",
            rol=rol,
        )
        self.client = Client()

    def test_login_exitoso(self):
        resp = self.client.post(
            reverse("login"),
            data=json.dumps({
                "username": "tester",
                "password": "clave123"
            }),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("token", resp.json())
        self.assertEqual(resp.json()["username"], "tester")

    def test_login_password_incorrecta(self):
        resp = self.client.post(
            reverse("login"),
            data=json.dumps({
                "username": "tester",
                "password": "incorrecta"
            }),
            content_type="application/json"
        )
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.json()["success"], False)
        self.assertEqual(resp.json()["message"], "Credenciales incorrectas")

"""
# Crear un superusuario
usuario_superadmin = Usuario.objects.create_superuser(
    ci="987654321",  # Cédula de identidad
    email="superadmin@example.com",  # Email
    nombre="Carlos",  # Nombre
    apellido="Gómez",  # Apellido
    username="Test1"
    password="contraseña_superadmin"  # Contraseña
    token='568df9a67fasdfga78asdgfdg',  # Token de autenticación
)

print(f"Superusuario creado: {usuario_superadmin.get_full_name()}")

"""