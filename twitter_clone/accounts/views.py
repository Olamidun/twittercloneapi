from django.shortcuts import render, reverse
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import ListAPIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from accounts.serializers import UserRegistrationSerializer, LoginSerializer, UserSearchSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.filters import SearchFilter, OrderingFilter
from accounts.models import Account
from .utils import Util
from django.contrib.sites.shortcuts import get_current_site
import jwt
from django.conf import settings
from django.contrib import auth
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


# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def search_user(request):
#     if request.method == "GET":
#         search_query = request.GET.get("q")
#         if len(search_query) > 0:
#             search_results = Account.objects.filter(username__icontains=search_query).filter(email__icontains=search_query).distinct()
#             serializer = UserSearchSerializer(search_results, many=True)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         return Response('Field cannot be empty', status=status.HTTP_400_BAD_REQUEST)
#     return Response('Bad request method', status=status.HTTP_405_METHOD_NOT_ALLOWED)

class SearchView(ListAPIView):
    queryset = Account.objects.all()
    serializer_class = UserSearchSerializer
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated, )
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('username', )
    