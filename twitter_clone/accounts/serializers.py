# from accounts.models import UserProfile
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.models import Account
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
import jwt
from django.conf import settings
class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}


    def validate(self, data):
        password = data.get('password')
        if len(password) <= 5:
            raise serializers.ValidationError({'Password Error': 'Your password must be greater than 5 characters'})
        return data


    def create(self, validated_data):
        # user = User(
        #     email=validated_data['email'],
        #     username=validated_data['username'],
        # )
        # user.set_password(validated_data['password'])
        # user.save()
        # Token.objects.create(user=user)
        return Account.objects.create_user(username=validated_data['username'], email=validated_data['email'], password=validated_data['password'])
    


class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(read_only=True)
    email = serializers.EmailField(required=True)
    date_joined = serializers.DateTimeField(read_only=True)
    active = serializers.BooleanField(read_only=True)
    password = serializers.CharField(write_only=True, required=True)
    tokens = serializers.CharField(read_only=True)

    class Meta:
        model = Account
        fields = ['email', 'password', 'username',  'date_joined', 'active', 'tokens']


    def validate(self, data):
        email = data['email']
        password = data['password']
        user = authenticate(email=email, password=password)
        
        
        if not user:
            raise serializers.ValidationError({"error": "Invalid login details, try again"})
        
        if not user.is_verified:
            raise AuthenticationFailed("Your Email account is not verified")

        if not user.is_active:
            raise AuthenticationFailed("Account is not active yet, please check your mailbox for email verification link")
        res = {
            "email": user.email,
            "username": user.username,
            "date_joined": user.date_joined,
            "active": user.is_active,
            "tokens": user.token
        }
        return res



# class UserProfileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UserProfile
#         fields = ['user', 'date_joined', 'profile_image', 'number_of_followers', 'number_of_followings']