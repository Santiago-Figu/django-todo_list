from django.shortcuts import render

# Create your views here.
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer

class UserCreateView(generics.CreateAPIView):
    """
    Endpoint para registro de nuevos usuarios.
    Permite: POST /api/users/register/
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]  # Permitir acceso sin autenticación

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
    # permission_classes = [permissions.IsAuthenticated]  # Requiere autenticación
    permission_classes = [permissions.AllowAny]

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
    permission_classes = [permissions.AllowAny]

    def perform_update(self, serializer):
        # Lógica adicional antes de actualizar (opcional)
        instance = self.get_object()
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": "Usuario eliminado correctamente."},
            status=status.HTTP_204_NO_CONTENT
        )