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
        required=True
    )
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'completed', 'created_at', 'completed_at', 'assigned_user', 'created_by' ]
        read_only_fields = ['id', 'created_at', 'completed_at', 'created_by']

    def validate(self, attrs):
        """
        Valida los datos ingresados por el usuario para crear una tarea.
        """
        logger.info("Validando datos")
        required_attributes = ['title', 'assigned_user']
    
        for attribute in required_attributes:
            if not attrs.get(attribute):
                raise serializers.ValidationError({attribute: "Favor de ingresar un valor."})
            
        attrs['title'] = clear_input_characters(attrs['title'])
        attrs['description'] = clear_input_characters(attrs['description'])

        if attrs.get('completed') and not attrs.get('completed_at'):
            attrs['completed_at'] = timezone.now()
        
        return attrs
    
    def to_representation(self, instance):
        logger.info("Extrayendo datos de las tareas")
        data = super().to_representation(instance)
        # data['assigned_user'] = UserSerializer(instance.assigned_user).data # serializa todos los datos del usuario
        user_data = {
            'id': instance.assigned_user.id,
            'name': instance.assigned_user.name,
            'lastname': instance.assigned_user.lastname,
            'team': instance.assigned_user.team
        }

        data['assigned_user'] = user_data
        return data