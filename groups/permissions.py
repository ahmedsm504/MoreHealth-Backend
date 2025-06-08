# عاملها عشان سبب وحيد اني اضيف الدليت و الابديت 
from rest_framework import permissions

class IsGroupOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Allow GET/HEAD/OPTIONS for everyone
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.creator == request.user

class IsContentOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user