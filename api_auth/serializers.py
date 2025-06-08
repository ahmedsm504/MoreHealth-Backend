from rest_framework import serializers 
from .models import User, DoctorProfile
from django.core.exceptions import ValidationError  # Add this import
from django.db import IntegrityError 
from django.core.validators import validate_email
class UserSerializer(serializers.ModelSerializer): 
    class Meta: 
        model = User 
        fields = ('id', 'username', 'email', 'password', 'age', 'gender', 'phone', 'type', 'city', 'medical_insurance', 'region' ,   'profile_picture')
        extra_kwargs = {'password': {'write_only': True},
                        
         'email': {
            #  'read_only': True ,
               'required': True,
                'allow_blank': False
             }
                        }
    def validate_email(self, value):
        value = value.strip().lower()
        if not value:
            raise serializers.ValidationError("Email cannot be empty")
        
        try:
            validate_email(value)
        except ValidationError:
            raise serializers.ValidationError("Enter a valid email address")
            
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered")
            
        return value

    def create(self, validated_data):
        try:
            user = User.objects.create_user(**validated_data)
            return user
        except IntegrityError as e:
            if 'email' in str(e):
                raise serializers.ValidationError({'email': 'This email is already registered'})
            raise
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        return super().update(instance, validated_data)

        

# serializers.py
class DoctorSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=True)

    class Meta:
        model = DoctorProfile
        fields = ('user', 'specialization', 'practice_permit' , 'verify_Doctor')

    def validate(self, attrs):
        email = attrs['user'].get('email', '').strip()
        if not email:
            raise serializers.ValidationError("Email is required")
        return attrs
    
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        
        # Use the validated email from UserSerializer
        user_serializer = UserSerializer(data=user_data)
        user_serializer.is_valid(raise_exception=True)
        
        try:
            user = user_serializer.save(type='doctor')
            return DoctorProfile.objects.create(user=user, **validated_data)
        except IntegrityError as e:
            if 'email' in str(e):
                raise serializers.ValidationError({'email': 'This email is already registered'})
            raise