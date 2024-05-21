from rest_framework import permissions
import logging


class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        user = request.user
        is_manager = (
            user
            and user.is_authenticated
            and user.groups.filter(name="Managers").exists()
        )
        is_superuser = user and user.is_superuser

        return is_manager or is_superuser


class IsDeliveryCrew(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        user = request.user
        is_manager = (
            user and user.is_authenticated and user.groups.filter(name="Crew").exists()
        )
        is_superuser = user and user.is_superuser

        return is_manager or is_superuser
