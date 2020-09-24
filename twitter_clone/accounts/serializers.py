# from accounts.models import UserProfile
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
import jwt
from django.conf import settings
class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}


    def validate(self, data):
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({'email': {'email already exist'}})
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError({'username': {'username already exist'}})
        return super().validate(data)


    def create(self, validated_data):
        # user = User(
        #     email=validated_data['email'],
        #     username=validated_data['username'],
        # )
        # user.set_password(validated_data['password'])
        # user.save()
        # Token.objects.create(user=user)
        return User.objects.create_user(username=validated_data['username'], email=validated_data['email'], password=validated_data['password'])
    


class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(read_only=True)
    date_joined = serializers.DateTimeField(read_only=True)
    active = serializers.BooleanField(read_only=True)
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'date_joined', 'active']

    # def token(self, data):
    #     user = User.objects.get(email=data['email'])
    #     refresh  = RefreshToken.for_user(user)
    #     return {
    #         "refresh": str(refresh),
    #         "access": str(refresh.access_token)
    #     }

    def validate(self, data):
        username = data['username']
        password = data['password']
        user = authenticate(username=username, password=password)
        
        if not user.is_active:
            raise AuthenticationFailed("Account is not active yet, please check your mailbox for email verification link")
        if not user:
            raise serializers.ValidationError({"error": "Invalid login details, try again"})

        return {
            "email": user.email,
            "username": user.username,
            "date_joined": user.date_joined,
            "active": user.is_active, 
            "token": token
        }



# class UserProfileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UserProfile
#         fields = ['user', 'date_joined', 'profile_image', 'number_of_followers', 'number_of_followings']