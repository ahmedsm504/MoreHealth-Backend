from rest_framework import permissions
from .models import ChatRoom

class IsRoomParticipant(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Check if user is a participant in the room
        return request.user in obj.participants.all()

    def has_permission(self, request, view):
        # For list/create actions, check through the room ID in URL
        if 'room_id' in view.kwargs:
            room_id = view.kwargs['room_id']
            try:
                room = ChatRoom.objects.get(id=room_id)
                return request.user in room.participants.all()
            except ChatRoom.DoesNotExist:
                return False
        return True