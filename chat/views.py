


from django.contrib.auth import get_user_model  # Add this import
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.shortcuts import get_object_or_404
from .models import ChatRoom, Message, Friendship
from .serializers import (
    UserSerializer,
    MessageSerializer,
    ChatRoomSerializer,
    FriendshipReadSerializer,
    FriendshipWriteSerializer
)
from .permissions import IsRoomParticipant
from django.db.models import Count


User = get_user_model()


class ChatRoomListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        chat_rooms = ChatRoom.objects.filter(participants=request.user)\
            .prefetch_related('participants')\
            .distinct()
        serializer = ChatRoomSerializer(
            chat_rooms,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)


class StartPrivateChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        other_user = get_object_or_404(User, id=user_id)
        if other_user == request.user:
            return Response(
                {"detail": "Cannot start chat with yourself."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check for existing private chat between the two users
        existing_chat = ChatRoom.objects.annotate(
            num_participants=Count('participants')
        ).filter(
            participants=request.user
        ).filter(
            participants=other_user
        ).filter(
            num_participants=2
        ).first()

        if existing_chat:
            return Response({
                'room_id': existing_chat.id,
                'created': False
            }, status=status.HTTP_200_OK)
        else:
            # Create new private chat
            chat_room = ChatRoom.objects.create()
            chat_room.participants.add(request.user, other_user)
            return Response({
                'room_id': chat_room.id,
                'created': True
            }, status=status.HTTP_201_CREATED)
class MessageView(APIView):
    # permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsRoomParticipant]

    def get_queryset(self):
        return Message.objects.filter(
            room_id=self.kwargs['room_id']
        ).select_related('sender').order_by('timestamp')

    def perform_create(self, serializer):
        room = ChatRoom.objects.get(id=self.kwargs['room_id'])
        serializer.save(room=room, sender=self.request.user)

    def get(self, request, room_id):
        room = get_object_or_404(ChatRoom, id=room_id)
        if request.user not in room.participants.all():
            return Response(
                {"detail": "Not authorized."},
                status=status.HTTP_403_FORBIDDEN
            )
        messages = Message.objects.filter(room=room)\
            .select_related('sender')\
            .order_by('timestamp')
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    def post(self, request, room_id):
        room = get_object_or_404(ChatRoom, id=room_id)
        if request.user not in room.participants.all():
            return Response(
                {"detail": "Not a participant of this chat room."},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(room=room, sender=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FriendshipView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        friends = Friendship.objects.filter(
            (Q(sender=request.user) | Q(receiver=request.user)),
            status='accepted'
        )
        serializer = FriendshipReadSerializer(friends, many=True)
        return Response(serializer.data)

    def post(self, request, user_id = None):
        if not user_id:
            return Response(
                {"detail": "User ID required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        receiver = get_object_or_404(User, id=user_id)
        if receiver == request.user:
            return Response(
                {"detail": "Cannot send request to yourself."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if Friendship.objects.filter(
            Q(sender=request.user, receiver=receiver) |
            Q(sender=receiver, receiver=request.user),
            status__in=['pending', 'accepted']
        ).exists():
            return Response(
                {"detail": "Friend request already exists."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = FriendshipWriteSerializer(data={
            'receiver': receiver.id
        }, context={'request': request})
        
        if serializer.is_valid():
            friendship = serializer.save()
            return Response(
                FriendshipReadSerializer(friendship).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FriendRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request ,  pk=None):
        if pk:
            # Get single request detail
            friendship = get_object_or_404(
                Friendship,
                id=pk,
                receiver=request.user
            )
            serializer = FriendshipReadSerializer(friendship)
            return Response(serializer.data)
        pending_requests = Friendship.objects.filter(
            receiver=request.user,
            status='pending'
        )
        serializer = FriendshipReadSerializer(pending_requests, many=True)
        return Response(serializer.data)

    def patch(self, request, pk= None):
        if not pk:
            return Response(
                {"detail": "Request ID required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        friendship = get_object_or_404(
            Friendship,
            id=pk,
            receiver=request.user,
            status='pending'
        )
        action = request.data.get('action')
        
        if action == 'accept':
            friendship.status = 'accepted'
        elif action == 'reject':
            friendship.status = 'declined'
        else:
            return Response(
                {"detail": "Invalid action."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        friendship.save()
        return Response(FriendshipReadSerializer(friendship).data)