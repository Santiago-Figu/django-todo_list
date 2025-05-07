from django.shortcuts import redirect, render

# Create your views here.
from rest_framework.response import Response
from rest_framework import status, permissions, generics, serializers
from rest_framework.views import APIView
from utils.auth import JWTAuthentication
from utils.logger import LoggerConfig
from .models import User
from .serializers import PasswordChangeSerializer, UserSerializer
from .permissions import IsAdminTeam
from django.http import Http404
from rest_framework.exceptions import NotFound

logger = LoggerConfig("user_views", debug=True).get_logger()

class UserCreateView(generics.CreateAPIView):
    """
    Endpoint para registro de nuevos usuarios.
    Permite: POST /api/users/register/
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]  # Permitir acceso sin autenticación
    # permission_classes = [IsAdminTeam]  # Solo admin puede crear usuarios
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if str(request.data['team']).lower().strip() == 'admin':
            return Response(
                {"error": f"El valor '{request.data['team']}' para team no es valido, verificar"},
                status=status.HTTP_400_BAD_REQUEST
            )
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
        else:
            if self.request.query_params:
                raise NotFound('No se permiten "query parameters". Try /api/users/<id>/')
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
    lookup_url_kwarg = 'id'  # Esto es explícito sobre qué parámetro de URL usar
    # permission_classes = [permissions.IsAuthenticated]
    # permission_classes = [permissions.AllowAny]

    def get_permissions(self):
        """
        Asigna permisos dinámicos:
        - DELETE: Solo admin
        - Otros métodos: Sin restricción (o las que necesites)
        """
        logger.info(f"request: {self.request.method}")
        if self.request.method == 'DELETE':
            return [IsAdminTeam()]
        # return [permissions.AllowAny()] # solo para testing
        return [permissions.IsAuthenticated()]

    def perform_update(self, serializer):
        # Lógica adicional antes de actualizar (opcional)
        team_value = serializer.validated_data.get('team')
        payload = self.request.user
        logger.debug(f'Datos del token: {payload.team}')
        logger.debug(f'serializer.validated_data:{serializer.validated_data}')
    
        if team_value and str(team_value).lower() == "admin" and str(payload.team).lower() != "admin":
            raise serializers.ValidationError(
                {"team": "No puedes asignar el valor 'admin' al equipo."},
                code="invalid_team"
            )
        
        instance = self.get_object()
        logger.warning(f'Actualizando datos de: {instance.name}')
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": "Usuario eliminado correctamente."},
            status=status.HTTP_204_NO_CONTENT
        )
    
    def get_object(self):
        # Verifica si hay query params (ej: ?id=1) y lanza error si los hay
        if self.request.query_params:
            raise NotFound("No se permiten query parameters. Use /api/users/<id>/")
        
        # Fuerza a que el ID esté en la URL (si no, lanza 404)
        if 'id' not in self.kwargs:
            raise Http404("El ID debe estar en la URL: /api/users/<id>/")
    
        try:
            return User.objects.get(id=self.kwargs['id'])
            # return super().get_object()  para regresar los datos del usuario mediante los parametros sin manipular los datos
        except User.DoesNotExist:
            raise NotFound("Usuario no encontrado.")
        except ValueError:
            raise NotFound("El ID debe ser un número entero.")
            
class PasswordChangeView(generics.UpdateAPIView):
    serializer_class = PasswordChangeSerializer
    authentication_classes = [JWTAuthentication]
    # permission_classes = [permissions.AllowAny] # solo para testing
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.get_object()
        new_password = serializer.validated_data['new_password']
        old_password = serializer.validated_data['old_password']
        #Todo: conciderar realizar un metodo de cambio de contraseña basado en un codigo generado por correo
        try:
            if old_password == user.get_password():
                user.set_password(new_password)
                user.save()
            
                logger.info(f"Contraseña actualizada para usuario {user.username}")
                return Response(
                    {"detail": "Contraseña actualizada correctamente"},
                    status=status.HTTP_200_OK
                )
            else:
                message = f'El password anterior para el usuario {user.username} no coincide, validar datos'
                logger.info(message)
                return Response(
                    {"detail": message},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            message = f"Error interno al actualizar contraseña: {str(e)}"
            logger.error(message)
            return Response(
                {"detail": message},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )        