from django.urls import path
from . import views

urlpatterns = [
    path('login', views.login, name='auth-login'),
    path('signup', views.signup, name='auth-signup'),
    path('signup-doctor', views.signupDoctor, name='auth-signup-doctor'),
    path('test-token', views.test_token, name='auth-test-token'),
    
    
    path('update-user/', views.update_user, name='update-user'),
    path('delete-account/', views.delete_account, name='delete-account'),
    path('forgot-password/', views.forgot_password, name='forgot-password'),
    path('reset-password/', views.reset_password, name='reset-password'),
    # path('google-auth/', views.google_auth, name='google-auth'),
]