from django.urls import path
from .views import PasswordChangeView, UserCreateView, UserListView, UserDetailView

urlpatterns = [
    path('register/', UserCreateView.as_view(), name='user-register'),
    path('', UserListView.as_view(), name='user-list'),
    path('<int:id>/', UserDetailView.as_view(), name='user-detail'),
    path('change-password/', PasswordChangeView.as_view(), name='change-password'),
]