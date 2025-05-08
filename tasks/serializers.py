from datetime import timezone
from rest_framework import serializers

from tasks.models import Task
from users.models import User
from users.serializers import UserSerializer
from utils.validators import clear_input_characters
from utils.logger import LoggerConfig

logger =LoggerConfig(file_name="task_serializers", debug=True).get_logger()

class TaskSerializer(serializers.ModelSerializer):
    assigned_user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=True  # Obligatorio desde el serializador
    )
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'completed', 
            'created_at', 'completed_at', 'assigned_user', 
            'created_by'
        ]
        read_only_fields = [
            'id', 'created_at', 'completed_at', 
            'created_by'  # No se permite asignación directa
        ]

    def validate(self, attrs):
        """Validación personalizada"""
        if len(attrs.get('title', '').strip()) < 3:
            raise serializers.ValidationError(
                {"title": "El título debe tener al menos 3 caracteres."}
            )
            
        return attrs

    def to_representation(self, instance):
        """Formato de salida personalizado"""
        data = super().to_representation(instance)
        data['assigned_user'] = {
            'id': instance.assigned_user.id,
            'name': instance.assigned_user.name,
            'lastname': instance.assigned_user.name,
            'team': instance.assigned_user.team
        }
        data['created_by'] = {
            'id': instance.created_by.id,
            'name': instance.created_by.name,
            'lastname': instance.created_by.lastname,
            'team': instance.created_by.team
        }
        return data