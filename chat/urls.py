
from django.urls import path
from .views import (
    ChatRoomListView,
    StartPrivateChatView,
    MessageView,
    FriendshipView,
    FriendRequestView
)

urlpatterns = [
    path('chat-rooms/', ChatRoomListView.as_view(), name='chat-room-list'),
    path('start-chat/<int:user_id>/', StartPrivateChatView.as_view(), name='start-private-chat'),
    path('messages/<int:room_id>/', MessageView.as_view(), name='message-list'),
    
    # Friends endpoints
    path('friends/', FriendshipView.as_view(), name='friendship-list'),
    path('friends/<int:user_id>/', FriendshipView.as_view(), name='add-friend'),
    
    # Friend requests endpoints
    path('friend-requests/', FriendRequestView.as_view(), name='friend-requests-list'),
    path('friend-requests/<int:pk>/', FriendRequestView.as_view(), name='handle-friend-request'),
]