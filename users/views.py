from django.shortcuts import redirect, render

# Create your views here.
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework import status, permissions, generics
from rest_framework.views import APIView

from users.auth import JWTAuthentication
from users.utils import AESCipher
from utils.logger import LoggerConfig
from .models import User
from .serializers import UserSerializer, LoginSerializer
from utils.jwt_utils import TokenJwt
from .permissions import IsAdminTeam
from django.contrib.auth import authenticate

logger = LoggerConfig("user_views", debug=True).get_logger()

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]
    template_name = 'users/login2.html'
    
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
                raise Exception("Credenciales inválidas")
                
            token = TokenJwt().create_access_token({
                "user_id": user.id,
                "username": user.username,
                "team": user.team
            })
            
            if request.accepted_renderer.format == 'html':
                serializer = LoginSerializer()
                data_token, message = TokenJwt().validate_token(token)
                # print(f"data: {data_token}, {message}")
                return Response({
                    'serializer': serializer.data,
                    'token': token,
                    'show_token': True,
                    'debug_mode': False,
                    'token_debug': data_token,
                })
                
            return Response({"token": token})
            
        except Exception as e:
            serializer.add_error(None, str(e))
            return Response(
                {
                    'serializer': serializer,
                    'token': None,
                    'show_token': False
                },
                status=status.HTTP_401_UNAUTHORIZED
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
    
class UserCreateView(generics.CreateAPIView):
    """
    Endpoint para registro de nuevos usuarios.
    Permite: POST /api/users/register/
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # permission_classes = [permissions.AllowAny]  # Permitir acceso sin autenticación
    permission_classes = [IsAdminTeam]  # Solo admin puede crear usuarios
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

class UserListView(generics.ListAPIView):
    """
    Endpoint para listar todos los usuarios (solo lectura).
    Permite: GET /api/users/
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]  # Usa tu autenticación personalizada
    permission_classes = [permissions.IsAuthenticated]  # Requiere autenticación
    # permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        # Opcional: Filtrar usuarios por equipo (ej: ?team=Development)
        team = self.request.query_params.get('team')
        if team:
            return User.objects.filter(team__iexact=team)
        return super().get_queryset()

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    #/api/users/<id>/
    """
    Endpoint para ver, actualizar o eliminar un usuario específico.
    Permite:
    - GET
    - PATCH
    - DELETE
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'id'
    # permission_classes = [permissions.IsAuthenticated]
    # permission_classes = [permissions.AllowAny]

    def get_permissions(self):
        """
        Asigna permisos dinámicos:
        - DELETE: Solo admin
        - Otros métodos: Sin restricción (o las que necesites)
        """
        if self.request.method == 'DELETE':
            return [IsAdminTeam()]
        return []  # O [permissions.IsAuthenticated()] si quieres que todos los métodos requieran autenticación

    def perform_update(self, serializer):
        # Lógica adicional antes de actualizar (opcional)
        instance = self.get_object()
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        # Esta parte ya no necesita verificación adicional porque
        # el permiso IsAdminTeam ya la hizo
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": "Usuario eliminado correctamente."},
            status=status.HTTP_204_NO_CONTENT
        )