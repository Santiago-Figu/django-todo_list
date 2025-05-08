from django.db import models

# Create your models here.

from users.models import User

class Task(models.Model):
    """Modelo de tarea"""
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)  # Cambiado a TextField
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)  # auto_now_add para creación
    completed_at = models.DateTimeField(null=True, blank=True)
    assigned_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="assigned_tasks",
        null=True,  # Permite null si es necesario
        # Eliminado el default=1
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_tasks'
        # Eliminado el default=None
    )

    class Meta:
        db_table = 'tasks'
        app_label = 'tasks'

    def __str__(self):
        return self.title