from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from utils.jwt_utils import TokenJwt
from users.models import User

token_manager = TokenJwt()

class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION','')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
            
        try:
            token = auth_header.split()[1]
            payload, error = token_manager.validate_token(token)
            if error:
                raise AuthenticationFailed(error)
                
            user = User.objects.get(id=payload['user_id'])
            return (user, None)
            
        except User.DoesNotExist:
            raise AuthenticationFailed('Usuario no encontrado')
        except Exception as e:
            raise AuthenticationFailed(f'Error de autenticación: {str(e)}')