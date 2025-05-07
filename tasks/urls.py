from django.urls import path
from .views import TaskDetailView, TasksListView

urlpatterns = [
    path('', TasksListView.as_view(), name='task-list'),
    path('<int:id>/', TaskDetailView.as_view(), name='task-detail'),
]


