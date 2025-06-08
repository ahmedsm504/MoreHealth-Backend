# api_auth/views.py
import logging
import uuid
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import User, PasswordResetToken
from .serializers import UserSerializer, DoctorSerializer
from rest_framework.parsers import MultiPartParser, FormParser , JSONParser
from rest_framework.decorators import parser_classes

logger = logging.getLogger(__name__)

def _create_jwt_tokens(user):
    """Helper to generate JWT tokens."""
    refresh = RefreshToken.for_user(user)
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh)
    }

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """User authentication endpoint."""
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response(
            {"message": "Email and password are required"}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    user = User.objects.filter(email=email).first()
    
    if not user or not user.check_password(password):
        return Response(
            {"message": "Invalid credentials"}, 
            status=status.HTTP_401_UNAUTHORIZED
        )

    tokens = _create_jwt_tokens(user)
    serializer = UserSerializer(user)
    
    return Response({
        **tokens,
        'user': serializer.data,
        'message': 'Login successful'
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    """User registration endpoint."""
    serializer = UserSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            serializer.errors, 
            status=status.HTTP_400_BAD_REQUEST
        )

    with transaction.atomic():
        user = serializer.save()
        user.set_password(request.data["password"])
        user.save()
        tokens = _create_jwt_tokens(user)
    
    return Response({
        **tokens,
        "user": serializer.data,
        "message": "Account created successfully"
    }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([AllowAny])
def signupDoctor(request):  # Maintain original name for URL compatibility
    """Doctor registration endpoint."""
    serializer = DoctorSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            serializer.errors, 
            status=status.HTTP_400_BAD_REQUEST
        )

    with transaction.atomic():
        doctor_profile = serializer.save()
        tokens = _create_jwt_tokens(doctor_profile.user)
    
    return Response({
        **tokens,
        'doctor_profile': serializer.data,
        'message': 'Doctor account created successfully'
    }, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def test_token(request):
    """Token validation endpoint."""
    return Response(f"Authenticated as {request.user.email}")


@api_view(['PUT', 'PATCH'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def update_user(request):
    """User profile update endpoint."""
    user = request.user
    
    serializer = UserSerializer(
        instance=user,
        data=request.data,
        partial=True,
        context={'request': request}  # Add request context
    )
    
    if serializer.is_valid():
        serializer.save()
        return Response(
            UserSerializer(user, context={'request': request}).data,
            status=status.HTTP_200_OK
        )
        
    return Response(
        serializer.errors, 
        status=status.HTTP_400_BAD_REQUEST
    )

@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_account(request):
    """Account deletion endpoint."""
    request.user.delete()
    return Response(
        {"message": "Account deleted successfully"}, 
        status=status.HTTP_204_NO_CONTENT
    )

@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    """Password reset initiation endpoint."""
    email = request.data.get('email')
    user = User.objects.filter(email=email).first()
    
    if user:
        token = uuid.uuid4().hex
        expires_at = timezone.now() + timedelta(hours=1)
        
        PasswordResetToken.objects.update_or_create(
            user=user,
            defaults={'token': token, 'expires_at': expires_at}
        )
        
        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
        subject = "Password Reset Request"
        html_message = render_to_string('password_reset_email.html', {
            'user': user,
            'reset_link': reset_link,
            'expiration_hours': 1
        })
        plain_message = strip_tags(html_message)
        
        try:
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=html_message,
                fail_silently=False,
            )
            logger.info(f"Password reset email sent to {user.email}")
        except Exception as e:
            logger.error(f"Email sending failed: {str(e)}")
            return Response(
                {"message": "Failed to send reset email"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    return Response(
        {"message": "If an account exists, a reset link has been sent"}, 
        status=status.HTTP_200_OK
    )
    
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def reset_password(request):
    if request.method == 'GET':
        # Verify token validity
        token = request.GET.get('token')
        if not token:
            return Response({"message": "Token is required"}, status=400)
            
        try:
            reset_token = PasswordResetToken.objects.get(token=token)
            if reset_token.is_expired():
                return Response({"message": "Token has expired"}, status=400)
            return Response({"message": "Token is valid"}, status=200)
        except PasswordResetToken.DoesNotExist:
            return Response({"message": "Invalid token"}, status=400)

    elif request.method == 'POST':
        # Handle password reset
        token = request.data.get('token')
        new_password = request.data.get('new_password')
        
        if not token or not new_password:
            return Response({"message": "Token and password required"}, status=400)
        
        try:
            reset_token = PasswordResetToken.objects.get(token=token)
            if reset_token.is_expired():
                return Response({"message": "Expired token"}, status=400)
            
            validate_password(new_password, reset_token.user)
            reset_token.user.set_password(new_password)
            reset_token.user.save()
            reset_token.delete()
            return Response({"message": "Password reset successful"})
            
        except ValidationError as e:
            return Response({"message": e.messages}, status=400)
        except PasswordResetToken.DoesNotExist:
            return Response({"message": "Invalid token"}, status=400)
    """Password reset completion endpoint."""
    token = request.data.get('token')
    new_password = request.data.get('new_password')
    
    if not token or not new_password:
        return Response(
            {"message": "Token and password required"}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    reset_token = PasswordResetToken.objects.filter(token=token).first()
    
    if not reset_token or reset_token.is_expired():
        return Response(
            {"message": "Invalid or expired token"}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        validate_password(new_password, reset_token.user)
        reset_token.user.set_password(new_password)
        reset_token.user.save()
        reset_token.delete()
        return Response({"message": "Password reset successful"})
    
    except ValidationError as e:
        return Response(
            {"message": e.messages}, 
            status=status.HTTP_400_BAD_REQUEST
        )