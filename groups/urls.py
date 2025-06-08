from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.GroupListCreateView.as_view(), name='group-list'),
    path('<int:pk>/', views.GroupDetailView.as_view(), name='group-detail'),
    path('<int:pk>/join/', views.ToggleMembershipView.as_view(), name='toggle-membership'),
    path('<int:group_pk>/questions/', views.QuestionListCreateView.as_view(), name='question-list'),
    
    path('questions/<int:pk>/', views.QuestionDetailView.as_view(), name='question-detail'),
   path('questions/', views.QuestionListView.as_view(), name='question-list'), 
   
    path('questions/<int:question_pk>/comments/', views.CommentListCreateView.as_view(), name='comment-list'),
    

    path('comments/<int:parent_pk>/replies/', views.ReplyListView.as_view(), name='reply-create'),
    # Comment detail routes (edit/delete)
    path('comments/<int:pk>/', views.CommentDetailView.as_view(), name='comment-detail'),
    
    # Reply list/create
    path('comments/<int:parent_pk>/replies/', views.ReplyListView.as_view(), name='reply-list-create'),

    
    path('upvote/<str:model_type>/<int:pk>/', views.UpvoteView.as_view(), name='toggle-upvote'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)