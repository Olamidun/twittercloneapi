from accounts.models import Profile
# from tweets.models import Follow
from rest_framework import serializers
# from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from accounts.models import Account
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
import jwt
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import DjangoUnicodeDecodeError, force_str, smart_bytes, smart_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
# from django.contrib.sites.shortcuts import get_current_site
# from django.urls import reverse

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
    tokens = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = ['email', 'password', 'username',  'date_joined', 'active', 'tokens']

    def get_tokens(self, obj):
        user = Account.objects.get(email=obj['email'])
        return {
            "access": user.token()['access'],
            "refresh": user.token()['refresh'],
        }


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


class LogOutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_messages = {
        'bad_token': 'Token is expired or invalid'
    }

    def validate(self, data):
        self.token = data['refresh']
        return data

    def save(self,  **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            self.fail('bad_token')


class PasswordRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    redirect_url = serializers.CharField(max_length=1000, required=False)

    class Meta:
        fields = ['email']

    

class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=6, write_only=True)
    token = serializers.CharField(min_length=1, write_only=True)
    uidb64 = serializers.CharField(min_length=1, write_only=True)

    class Meta:
        fields = ['password', 'token', 'uidb64']

    def validate(self, data):
        try:
            password_ = data['password']
            token_ = data['token']
            uidb64_ = data['uidb64']

            id = force_str(urlsafe_base64_decode(uidb64_))
            user = Account.objects.get(id=id)
            print(id)
            print(user)
            print(uidb64_)
            print(password_)

            if not PasswordResetTokenGenerator().check_token(user, token_):
                raise AuthenticationFailed('The reset link is invalid', 401)
            user.set_password(password_)
            user.save()
        except DjangoUnicodeDecodeError:
            raise AuthenticationFailed('The reset link is invalid', 401)
        return super().validate(data)

class UserSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        exclude = ['password', 'groups', 'user_permissions', 'is_superuser', 'is_admin', 'is_staff']


class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField('get_username')
    class Meta:
        model = Profile
        fields = ['user', 'bio', 'location', 'website', 'profile_image', 'number_of_tweets', 'number_of_followers', 'number_of_following']
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

    # def get_followers(self, follow):
    #     for follower in follow.objects.all:
    #         followers = follower.followers.username
    #     return followers
 


# class FollowSerializer(serializers.ModelSerializer):
#     followers = serializers.SerializerMethodField('get_followers')
#     following = serializers.SerializerMethodField('get_following')

#     class Meta:
#         model = Follow
#         fields = ['followers', 'following']

    
#     def get_followers(self, follow):
#         followers = follow.followers.id
#         return followers

#     def get_following(self, follow):
#         following = follow.following.id
#         return following