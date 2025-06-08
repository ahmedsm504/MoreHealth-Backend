# serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import ChatRoom, Message, Friendship

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'room', 'sender', 'content', 'timestamp']
        read_only_fields = ['sender', 'timestamp', 'room']

class ChatRoomSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    other_user = serializers.SerializerMethodField()
    is_private = serializers.BooleanField(read_only=True) 
    
    class Meta:
        model = ChatRoom
        fields = ['id', 'participants', 'created_at', 'is_private', 'other_user']
        read_only_fields = ['created_at', 'is_private']

    def get_other_user(self, obj):
        request = self.context.get('request')
        if obj.is_private:
            return UserSerializer(
                obj.participants.exclude(id=request.user.id).first(),
                context=self.context
            ).data
        return None

class FriendshipReadSerializer(serializers.ModelSerializer):
    sender = UserSerializer()
    receiver = UserSerializer()

    class Meta:
        model = Friendship
        fields = ['id', 'sender', 'receiver', 'status']
        read_only_fields = ['status']

class FriendshipWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friendship
        fields = ['receiver']
    def create(self, validated_data):
        # Get sender from request context
        sender = self.context['request'].user
        receiver = validated_data['receiver']
        
        return Friendship.objects.create(
            sender=sender,
            receiver=receiver,
            status='pending'
        )