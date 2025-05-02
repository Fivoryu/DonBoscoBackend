set -o errexit

echo "Instalando dependencias..."
pip install -r requirements.txt

echo "Recopilando archivos estáticos..."
python manage.py collectstatic --no-input

if [ -z "$RENDER_EXTERNAL_HOSTNAME" ]; then
  echo "La variable RENDER_EXTERNAL_HOSTNAME no está definida."
else
  echo "RENDER_EXTERNAL_HOSTNAME está definida como: $RENDER_EXTERNAL_HOSTNAME"
fi

echo "Ejecutando migraciones..."
python manage.py migrate || { echo "Error al ejecutar las migraciones"; exit 1; }

# Crear superusuario personalizado si no existe
if [ "$CREATE_SUPERUSER" = "true" ]; then
  echo "Creando superusuario..."
  python manage.py shell << END
from django.contrib.auth import get_user_model
from usuarios.models import Rol

User = get_user_model()

# Crear rol de SuperAdmin si no existe
rol_superadmin, created = Rol.objects.get_or_create(
    nombre='SuperAdmin',
    defaults={'descripcion': 'Rol de superadministrador del sistema'}
)

if not User.objects.filter(username="${DJANGO_SUPERUSER_USERNAME}").exists():
    usuario_superadmin = User.objects.create_superuser(
        ci="987654321",  # Cédula de identidad
        email="${DJANGO_SUPERUSER_EMAIL}",  # Email
        nombre="Carlos",  # Nombre
        apellido="Gómez",  # Apellido
        username="${DJANGO_SUPERUSER_USERNAME}",
        password="${DJANGO_SUPERUSER_PASSWORD}",  # Contraseña
        rol=rol_superadmin
    )
    print(f"Superusuario creado: {usuario_superadmin.get_full_name()}")
else:
    print("El superusuario ya existe")
END
fi