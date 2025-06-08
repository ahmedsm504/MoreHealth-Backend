from django.db import models
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db.models import Count

User = get_user_model()


class ChatRoom(models.Model):
    participants = models.ManyToManyField(User, related_name="chat_rooms" , db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    @property
    def is_private(self):
        """Check if chat is private (exactly 2 participants) with caching"""
        cache_key = f'chatroom_{self.id}_private_status'
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
            
        is_private = self.participants.count() == 2
        cache.set(cache_key, is_private, 300)
        return is_private

    def participants_count(self):
        return self.participants.count()
    
    @classmethod
    def get_or_create_private_chat(cls, user1, user2):
        # Find existing private chat using Count
        existing = cls.objects.filter(participants=user1)\
                             .filter(participants=user2)\
                             .annotate(num_participants=Count('participants'))\
                             .filter(num_participants=2)\
                             .first()
        
        if existing:
            return existing, False
            
        # Create new private chat
        new_room = cls.objects.create()
        new_room.participants.add(user1, user2)
        return new_room, True
class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

class Friendship(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_requests")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_requests")
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('declined', 'Declined')])
