from django.shortcuts import render

from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework import status, permissions
from rest_framework.views import APIView
from utils.logger import LoggerConfig
from users.models import User
from .serializers import LoginSerializer
from utils.jwt_utils import TokenJwt

# Create your views here.

logger = LoggerConfig("login_views", debug=True).get_logger()

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]
    template_name = 'login/login2.html'
    
    def get(self, request):
        serializer = LoginSerializer()
        return Response({
            'serializer': serializer.data,
            'token': None,
            'show_token': False,
            'content_type': request.content_type
        })
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                {
                    'serializer': serializer.data,
                    'token': None,
                    'show_token': False
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            username_or_email = serializer.validated_data['username']
            password = serializer.validated_data['password']
            
            user = self._authenticate_user(username_or_email, password)
            if not user:
                if request.accepted_renderer.format == 'html':
                    #para renderizado de la plantilla 
                    serializer.add_error(None, "Credenciales no validas, verificar")
                    return Response({
                        'errors': serializer.errors,
                    })
                else:
                    return Response(
                        {
                            "detail": "Credenciales no validas, verificar",
                        },
                        status=status.HTTP_401_UNAUTHORIZED
                    )
                
            token = TokenJwt().create_access_token({
                "user_id": user.id,
                "username": user.username,
                "team": user.team
            })
            
            if request.accepted_renderer.format == 'html':
                #para renderizado de la plantilla 
                serializer = LoginSerializer()
                data_token, message = TokenJwt().validate_token(token)
                return Response({
                    'serializer': serializer.data,
                    'token': token,
                    'show_token': True,
                    'debug_mode': False,
                    'token_debug': data_token,
                })
            else:
                # Para request de postman
                return Response({"token": token})
            
        except Exception as e:
            serializer.add_error(None, str(e))
            return Response(
                {
                    "detail": "Ocurrio un error inesperado, intente más tarde",
                    'errors': serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
    def _authenticate_user(self, username_or_email: str, raw_password: str):
        """Autenticación personalizada que busca por username o email cifrado"""
        try:
            # Buscar por username (no cifrado)
            user = User.objects.get(username=username_or_email)
            if user.get_password() == raw_password:
                return user
            return None
            
        except User.DoesNotExist:
            try:
                # Si no encuentra por username, busca en todos los usuarios
                # comparando emails descifrados
                #ToDo: esto no es eficiente, considerar agregar un campo hash para el email (email_hash)
                users = User.objects.all()
                for user in users:
                    try:
                        # Desciframos el email almacenado para comparar
                        decrypted_email = user.get_email()
                        if decrypted_email == username_or_email and user.get_password() == raw_password:
                            return user
                    except Exception as e:
                        logger.error(f"Error al descifrar email para usuario {user.username}: {str(e)}")
                        continue
                return None
                
            except Exception as e:
                logger.error(f"Error en autenticación: {str(e)}")
                return None