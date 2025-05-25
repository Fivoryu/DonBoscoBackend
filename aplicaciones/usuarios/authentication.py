from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from .models import MultiToken
from rest_framework.authentication import SessionAuthentication

class MultiTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth = request.headers.get('Authorization')
        if not auth or not auth.startswith("Token "):
            return None
        token_key = auth.split(" ")[1]
        try:
            token = MultiToken.objects.get(key=token_key)
        except MultiToken.DoesNotExist:
            raise exceptions.AuthenticationFailed("Token inválido.")
        return (token.user, token)
    
class CsrfExemptSessionAuthentication(BaseAuthentication):
    """
    Igual que SessionAuthentication pero sin enforce_csrf,
    de modo que los métodos POST/PUT/DELETE no requieren token CSRF.
    """
    def enforce_csrf(self, request):
        return  # no levanta excepción de CSRF
