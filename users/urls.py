from django.urls import path
from .views import LoginView, UserCreateView, UserListView, UserDetailView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('register/', UserCreateView.as_view(), name='user-register'),
    path('', UserListView.as_view(), name='user-list'),
    path('<int:id>/', UserDetailView.as_view(), name='user-detail'),
]