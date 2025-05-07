from django.shortcuts import redirect, render

# Create your views here.
from rest_framework import viewsets, status, permissions, generics
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from utils.auth import JWTAuthentication
from utils.logger import LoggerConfig

from tasks.models import Task
from tasks.serializers import TaskSerializer

logger =LoggerConfig(file_name="task_views", debug=True).get_logger()

class TasksListView(generics.ListAPIView):
    """
    Endpoint para listar y crear tareas
    GET /api/tasks/ - Lista tareas
    POST /api/tasks/ - Crea nueva tarea
    """
    queryset = Task.objects.select_related('assigned_user').all()
    serializer_class = TaskSerializer
    # authentication_classes = [JWTAuthentication]  # Usa tu autenticación personalizada
    # permission_classes = [permissions.IsAuthenticated]  # Requiere autenticación
    permission_classes = [permissions.AllowAny]
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
        """Asigna automáticamente el usuario logueado como creador"""
        logger.info("Creando lista de tareas")
        serializer.save(created_by=self.request.user)


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Endpoint para operaciones específicas
    GET /api/tasks/<id>/ - Detalle de tarea
    PUT/PATCH /api/tasks/<id>/ - Actualiza tarea
    DELETE /api/tasks/<id>/ - Elimina tarea
    """
    queryset = Task.objects.select_related('assigned_user').all()
    serializer_class = TaskSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer]  # Habilitar interfaz HTML
    lookup_field = 'id'

    def perform_update(self, serializer):
        """Actualiza la fecha de completado automáticamente"""
        if 'completed' in self.request.data and self.request.data['completed']:
            if not self.get_object().completed:
                serializer.save(completed_at=timezone.now())
                return
        serializer.save()