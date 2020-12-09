from django.shortcuts import redirect, reverse, get_object_or_404
from django.http import HttpResponsePermanentRedirect
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from accounts.serializers import (UserRegistrationSerializer, LoginSerializer, LogOutSerializer,
UserSearchSerializer, UserProfileSerializer,
PasswordRequestSerializer, SetNewPasswordSerializer)
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.filters import SearchFilter, OrderingFilter
from accounts.models import Account, Profile
from .utils import Util
from django.contrib.sites.shortcuts import get_current_site
import jwt
from django.conf import settings
from django.contrib import auth
from tweets.models import Follow, Stream, Tweets, TweetFile
from tweets.serializers import TweetSerializer, TweetFileSerializer
from django.db import transaction
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import DjangoUnicodeDecodeError, force_str, smart_bytes, smart_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from dotenv import load_dotenv
import os
# Create your views here.



load_dotenv()

front_end_url = os.getenv('FRONTEND_URL')

class CustomRedirect(HttpResponsePermanentRedirect):

    allowed_schemes = [front_end_url, 'http', 'https']


@api_view(['POST'])
def registration(request):
    serializer = UserRegistrationSerializer(data=request.data)
    response_data = {}
    if serializer.is_valid():
        serializer.save()
        user_data = serializer.data
        print(user_data)
        user = Account.objects.get(email=user_data['email'])
        token = RefreshToken.for_user(user).access_token

        current_site = get_current_site(request).domain

        relative_link = reverse('accounts:verify_email')

        absolute_url = f'http://{current_site}{relative_link}?token={str(token)}'

        email_body = f'Hi {user.username} use the link below to verify your email\n {absolute_url}'

        data = {'email_body': email_body, 'to_email': user.email, 'email_subject':'verify your email'}

        Util.send_email(data)
        response_data["response"] = "successfully registered new user, please check your mailbox to verify your email account"
        response_data["email"] = user.email
        response_data["username"] = user.username

        return Response(response_data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login(request):

    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        return Response(serializer.data, status=status.HTTP_200_OK)

        # return Response(serializer.data, status=status.HTTP_200_OK)

        # data["error"] = "invalid login details"
        # data["response"] = "Login not successful" 
        # return Response(data, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    serializer = LogOutSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response('You are now logged out', status=status.HTTP_204_NO_CONTENT)


@api_view(['GET',])
def verify_email(request):
    token = request.GET['token']
    try:
        payload = jwt.decode(token, settings.SECRET_KEY)
        user = Account.objects.get(id=payload['user_id'])
        if not user.is_verified:
            user.is_verified =True
            user.save()
        return Response({'email': 'Your account has been successfull activated'}, status=status.HTTP_200_OK)
    except jwt.ExpiredSignatureError:
        return Response({"error": 'Activation link has expired'}, status=status.HTTP_400_BAD_REQUEST)
    except jwt.exceptions.DecodeError:
        return Response({"error": 'Invalid token, request new one'}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
def password_reset(request):
    serializer = PasswordRequestSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.data['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(request).domain

            relative_link = reverse('accounts:reset-password', kwargs={'uidb64': uidb64, 'token': token})

            redirect_url = serializer.data.get('redirect_url', '')

            absolute_url = f'http://{current_site}{relative_link}'

            email_body = f'Hi {user.username}, you performed a password reset operation on our website, use the link below to reset your password\n {absolute_url}?redirect_url={redirect_url}'

            data = {'email_body': email_body, 'to_email': user.email, 'email_subject':'Reset your password'}

            Util.send_email(data)
            return Response({"success": f"Password reset mail has been sent to {email}"}, status=status.HTTP_200_OK)
        return Response('This user does not exist', status=status.HTTP_404_NOT_FOUND)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
def password_token_check(request, uidb64, token):
    redirect_url = request.GET.get('redirect_url')
    try:
        id = smart_str(urlsafe_base64_decode(uidb64))
        user = Account.objects.get(id=id)
        print(id)
        print(user)
        print(uidb64)
        if not PasswordResetTokenGenerator().check_token(user, token):

            if len(redirect_url) > 3:
                return CustomRedirect(f'{redirect_url}?token_valid=False')
            else:
                return CustomRedirect(f'{front_end_url}?token_valid=False')
            # return Response({'error': 'Token is not valid, please request a new one'}, status=status.HTTP_401_UNAUTHORIZED)
        if redirect_url and len(redirect_url) > 3:
            return CustomRedirect(f'{redirect_url}?token_valid=True&?message=Token is valid&?uidb64={uidb64}&?token={token}')
        else:
            return CustomRedirect(f'{front_end_url}?token_valid=False')
    except DjangoUnicodeDecodeError:
        return CustomRedirect(f'{redirect_url}?token_valid=False')


class SetNewPasswordView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"message": 'Your password has been reset, you can now login'}, status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    user = request.user
    followers_list = []
    following_list = []
    try:
        user_profile = user.profile
        follower_obj = Follow.objects.filter(following=user)
        following_obj = Follow.objects.filter(followers=user)

        number_of_tweets = Tweets.objects.filter(tweep=user).all().count()
        followers_qs = follower_obj.all()
        following_qs = following_obj.all()
        for following in following_qs:
            following_list.append(following.following.username)
        for follower in followers_qs:
            followers_list.append(follower.followers.username)
        number_of_followers = follower_obj.count()
        number_of_following = following_obj.count()

        user_profile.number_of_tweets = number_of_tweets
        user_profile.number_of_followers = number_of_followers
        user_profile.number_of_following = number_of_following
        user_profile.save()
    except Profile.DoesNotExist:
        return Response('There is no record found in the database', status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        serializer = UserProfileSerializer(user_profile)
        context = serializer.data
        context['following'] = following_list
        context['followers'] = followers_list
        return Response(context, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_405_METHOD_NOT_ALLOWED)



@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request, username):
    user = Account.objects.get(username=username)
    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        return Response('The User profile you want to edit cannot be found')
    if request.method == 'PUT':
        if profile.user == request.user:
            serializer = UserProfileSerializer(profile, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response('You are not authorized to edit this user profile')
    return Response(serializer.errors, status=status.HTTP_405_METHOD_NOT_ALLOWED)    

    
class SearchView(ListAPIView):
    queryset = Account.objects.all()
    serializer_class = UserSearchSerializer
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated, )
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('username', )


class FollowView(APIView):
    permission_classes = (IsAuthenticated, )
    @staticmethod    
    def post(request, username):
        user = request.user
        following = Account.objects.get(username=username)
        
        if user == following:
            return Response({
            "message": 'You cannot follow yourself'}, status=status.HTTP_400_BAD_REQUEST)
        elif Follow.objects.filter(following=following, followers=request.user).exists():
            return Response({
            "message": 'You are already following this user, you cannot follow more than once'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            f, created = Follow.objects.get_or_create(followers=user, following=following)
            tweets = Tweets.objects.all().filter(tweep=following)
            
            with transaction.atomic():
                for tweet in tweets:
                    stream = Stream(tweet=tweet, user=user, date=tweet.date_posted, following=following)
                    stream.save()
        return Response({
            "message": f'You are now following {following.username}',
        
        }, status=status.HTTP_200_OK)



class UnFollowView(APIView):
    permission_classes = (IsAuthenticated, )
    @staticmethod    
    def delete(request, username):
        user = request.user
        following = Account.objects.get(username=username)

        follow = Follow.objects.get(followers=user, following=following)
        
        if user == following:
            return Response({
            "message": 'You cannot unfollow yourself'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            follow.delete()
            Stream.objects.filter(following=following, user=user).all().delete()
            
        return Response({
            "message": f'{following.username} has been unfollowed',
        }, status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_tweets(request, username):
    user = Account.objects.get(username=username)
    try:
        tweets = Tweets.objects.filter(tweep=user).all()
    except Tweets.DoesNotExist:
        return Response('This user has no tweet', status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        serializer = TweetSerializer(tweets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_media(request, username):
    user = Account.objects.get(username=username)
    try:
        media = TweetFile.objects.filter(tweep=user).all()
    except TweetFile.DoesNotExist:
        return Response('This user has no media',status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        serializer = TweetFileSerializer(media, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            
