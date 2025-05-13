# usuarios/utils.py
from .models import Bitacora
from django.utils import timezone

def registrar_bitacora(usuario, ip, tabla_afectada, accion, descripcion=""):
    Bitacora.objects.create(
        usuario=usuario,
        ip=ip,
        hora_entrada=timezone.now(),
        tabla_afectada=tabla_afectada,
        accion=accion,
        descripcion=descripcion
    )