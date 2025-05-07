from django.db import models

# Create your models here.

from users.models import User

class Task(models.Model):
    """Modelo de tarea"""
    title = models.CharField(max_length=255)
    description = models.CharField(blank=True, null=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True)
    assigned_user = models.ForeignKey(
        User,
        on_delete = models.CASCADE,
        related_name="assigned_task",
        default=1
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_tasks',
        default=None
    )

    class Meta:
        db_table = 'tasks' #nombre de la tabla en la base de datos
        app_label = 'tasks'

    def __str__(self):
        return self.title