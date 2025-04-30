from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied

class IsAdminTeam(BasePermission):
    """Verifica si el usuario pertenece al equipo 'admin'"""
    def has_permission(self, request, view):
        if not request.user or not request.user.team:
            return False
        return request.user.team.lower() == "admin"