from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from .models import MultiToken

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
