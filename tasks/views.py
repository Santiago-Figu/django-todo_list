from datetime import timezone
from django.shortcuts import redirect, render

# Create your views here.
from rest_framework.response import Response
from rest_framework import status, permissions, generics, serializers
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.exceptions import NotFound, PermissionDenied
from django.http import Http404
from utils.auth import JWTAuthentication
from utils.logger import LoggerConfig

from tasks.models import Task
from tasks.serializers import TaskSerializer

logger =LoggerConfig(file_name="task_views", debug=True).get_logger()

class TaskCreateView(generics.CreateAPIView):
    """
    Endpoint para registro de nuevos usuarios.
    Permite: POST /api/tasks/create/
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    authentication_classes = [JWTAuthentication]  # Usa tu autenticación personalizada
    permission_classes = [permissions.IsAuthenticated]  # Requiere autenticación
    # permission_classes = [permissions.AllowAny]  # Permitir acceso sin autenticación
    # permission_classes = [IsAdminTeam]  # Solo admin puede crear usuarios

    def post(self, request, *args, **kwargs):
        """
        Maneja la creación de nuevas tareas
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Asignar usuario logueado como creador si no se especifica
        if not serializer.validated_data.get('assigned_user'):
            serializer.validated_data['assigned_user'] = request.user
        
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required"}, status=401)
        
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )
    
    def perform_create(self, serializer):
        """Asigna automáticamente el usuario creador"""
        # Asegura que assigned_user esté en los datos validados
        if 'assigned_user' not in serializer.validated_data:
            raise serializers.ValidationError(
                {"assigned_user": "Este campo es requerido."}
            )
        
        # Asigna el usuario actual como creador
        serializer.save(created_by=self.request.user)

class TasksListView(generics.ListAPIView):
    """
    Endpoint para listar tareas
    GET /api/tasks/ - Lista tareas
    """
    queryset = Task.objects.select_related('assigned_user').all()
    serializer_class = TaskSerializer
    authentication_classes = [JWTAuthentication]  # Usa tu autenticación personalizada
    permission_classes = [permissions.IsAuthenticated]  # Requiere autenticación
    # permission_classes = [permissions.AllowAny]
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer]  # Habilitar interfaz HTML

    def get_queryset(self):
        """Filtrado opcional"""
        logger.info("Cargando lista de tareas")
        queryset = super().get_queryset()

        if user_id := self.request.query_params.get('user_id'):
            queryset = queryset.filter(assigned_user=user_id)

         # Filtro por estado
        if completed := self.request.query_params.get('completed'):
            if completed.lower() in ['true', 'false']:
                queryset = queryset.filter(completed=(completed.lower() == 'true'))
                
        return queryset


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Endpoint para operaciones específicas
    - Admins pueden ver/modificar/eliminar cualquier tarea
    - Usuarios normales solo pueden operar con tareas propias o asignadas
    GET /api/tasks/<id>/ - Detalle de tarea
    PUT/PATCH /api/tasks/<id>/ - Actualiza tarea
    DELETE /api/tasks/<id>/ - Elimina tarea
    """
    serializer_class = TaskSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer]  # Habilitar interfaz HTML
    lookup_field = 'id'
    lookup_url_kwarg = 'id'  # Esto es explícito sobre qué parámetro de URL usar

    def get_object(self):
        # Validación de parámetros de URL
        if self.request.query_params:
            raise NotFound("No se permiten query parameters. Use /api/tasks/<id>/")
        
        if 'id' not in self.kwargs:
            raise Http404("El ID debe estar en la URL: /api/tasks/<id>/")

        try:
            task_id = self.kwargs['id']
            task = Task.objects.select_related('assigned_user', 'created_by').only('id', 'title', 'completed', 'assigned_user__id', 'created_by__id').get(id=task_id)  
            # Acceso para admin
            if self.request.user.team == 'admin':
                return task
                
            # Verificar permisos para usuarios normales
            if task.assigned_user == self.request.user or task.created_by == self.request.user:
                return task
                
            # Si no cumple ninguna condición anterior
            raise PermissionDenied(
                "No tienes permiso para acceder a esta tarea. "
                "Solo puedes acceder a tareas asignadas o creadas por ti."
            )
            
        except Task.DoesNotExist:
            raise NotFound("Tarea no encontrada.")
        except ValueError:
            raise NotFound("El ID debe ser un número entero.")
        
    def perform_update(self, serializer):
        """Actualiza completed_at si se marca como completada"""
        if 'completed' in serializer.validated_data and serializer.validated_data['completed']:
            if not serializer.instance.completed:
                serializer.validated_data['completed_at'] = timezone.now()
        super().perform_update(serializer)

    def get_queryset(self):
        """Sobrescribimos para que el filtro funcione en BrowsableAPI"""
        return Task.objects.select_related('assigned_user', 'created_by').all()