from accounts.models import Profile
from tweets.models import Follow
from rest_framework import serializers
# from rest_framework.response import Response
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
    
        return Account.objects.create_user(username=validated_data['username'], email=validated_data['email'], password=validated_data['password'])
    

class EmailVerificationSerializer(serializers.ModelSerializer):
    tokens = serializers.CharField(max_length=555)

    class Meta:
        model = Account
        fields = ['tokens']


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



class UserSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        exclude = ['password', 'groups', 'user_permissions', 'is_superuser', 'is_admin', 'is_staff']


class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField('get_username')
    class Meta:
        model = Profile
        fields = ['user', 'bio', 'location', 'website', 'profile_image']
        extra_kwargs = {
            "website": {
                "required": False
            },
            "location": {
                "required": False
            }
        }

    def get_username(self, profile):
        user = profile.user.username
        return user


class FollowSerializer(serializers.ModelSerializer):
    followers = serializers.SerializerMethodField('get_followers')
    following = serializers.SerializerMethodField('get_following')

    class Meta:
        model = Follow
        fields = ['followers', 'following']

    
    def get_followers(self, follow):
        followers = follow.followers.username
        return followers

    def get_following(self, follow):
        following = follow.following.username
        return following