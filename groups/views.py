from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from .models import Group, Question, Comment
from .serializers import GroupSerializer, QuestionSerializer, CommentSerializer , GroupFilter
from .permissions import IsGroupOwner, IsContentOwner # عشان اضيف المسح و التعديل 
import datetime 

from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter, OrderingFilter 
from django.db.models import Count 



class GroupListCreateView(generics.ListCreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    filter_backends = [filters.DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = GroupFilter
    
    search_fields = [
        'name', 
        'description',
        'tags__name',  # For exact tag matches
        'creator__username'  # Search by creator username
    ]
    ordering_fields = ['created_at', 'name', 'members_count']
    ordering = ['-created_at']  # Default ordering

    def get_queryset(self):
        return Group.objects.annotate(members_count=Count('members'))

    def perform_create(self, serializer):
        group = serializer.save(creator=self.request.user)
        group.members.add(self.request.user)
        

class GroupDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsGroupOwner]

class ToggleMembershipView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        group = get_object_or_404(Group, pk=pk)
        user = request.user
        if user in group.members.all():
            group.members.remove(user)
            return Response({'status': 'removed'})
        else:
            group.members.add(user)
            return Response({'status': 'added'})
        

class QuestionListView(generics.ListCreateAPIView):
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'upvotes_count']
    ordering = ['-created_at']

    def get_queryset(self):
        return Question.objects.annotate(
            upvotes_count=Count('upvotes'))
    # def get_queryset(self):
    #     return Question.objects.filter(
    #         group_id=self.kwargs['group_pk']
    #     ).annotate(
    #         upvotes_count=Count('upvotes'))

class QuestionListCreateView(generics.ListCreateAPIView):
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'upvotes_count']
    ordering = ['-created_at']

    def get_queryset(self):
        return Question.objects.annotate(
            upvotes_count=Count('upvotes'))

    def get_queryset(self):
        return Question.objects.filter(group_id=self.kwargs['group_pk'])

    def perform_create(self, serializer):
        group = get_object_or_404(Group, pk=self.kwargs['group_pk'])
        serializer.save(user=self.request.user, group=group)

class QuestionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsContentOwner]
# Add this view for comment detail operations
class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsContentOwner]

    def perform_update(self, serializer):
        # Automatically update the timestamp on edit
        
        serializer.save(updated_at=datetime.datetime.now()) 

# Modified CommentListCreateView
class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]  # Remove IsContentOwner from here

    def get_queryset(self):
        return Comment.objects.filter(
            question_id=self.kwargs['question_pk'],
            parent__isnull=True
        ).select_related('user').prefetch_related('replies')

    def perform_create(self, serializer):
        question = get_object_or_404(Question, pk=self.kwargs['question_pk'])
        serializer.save(user=self.request.user, question=question)

# Updated ReplyListView
class ReplyListView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        parent = get_object_or_404(Comment, pk=self.kwargs['parent_pk'])
        return Comment.objects.filter(parent=parent).order_by('-created_at')

    def perform_create(self, serializer):
        parent = get_object_or_404(Comment, pk=self.kwargs['parent_pk'])
        serializer.save(
            user=self.request.user,
            parent=parent,
            question=parent.question
        )

class UpvoteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, model_type, pk):
        models = {'question': Question, 'comment': Comment}
        model = models[model_type]
        obj = get_object_or_404(model, pk=pk)
        user = request.user
        if user in obj.upvotes.all():
            obj.upvotes.remove(user)
            return Response({'status': 'removed'})
        else:
            obj.upvotes.add(user)
            return Response({'status': 'added'})