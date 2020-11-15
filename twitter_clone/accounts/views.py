from django.shortcuts import render, reverse, get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import ListAPIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from accounts.serializers import (UserRegistrationSerializer, LoginSerializer, 
UserSearchSerializer, UserProfileSerializer, FollowSerializer)
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.filters import SearchFilter, OrderingFilter
from accounts.models import Account, Profile
from .utils import Util
from django.contrib.sites.shortcuts import get_current_site
import jwt
from django.conf import settings
from django.contrib import auth
from tweets.models import Tweets, Follow, Stream
from django.db import transaction
# Create your views here.


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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    user = request.user
    try:
        user_profile = user.user_profile
    except Profile.DoesNotExist:
        return Response('There is no record found in the database', status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        serializer = UserProfileSerializer(user_profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
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


@api_view(['POST',])
@permission_classes([IsAuthenticated])
def follow(request, username):
    user = request.user
    following = get_object_or_404(Account, username=username)

    # f, created = Follow.objects.get_or_create(followers=user, following=following)
    
    if request.method == 'POST':
        serializer = FollowSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(followers=user)
            tweets = Tweets.objects.all().filter(tweep=following)[:5]
            with transaction.atomic():
                for tweet in tweets:
                    stream = Stream(tweet=tweet, user=user, date=tweet.date_posted, following=following)
                    stream.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(serializer.errors, status=status.HTTP_405_METHOD_NOT_ALLOWED)

            
            
