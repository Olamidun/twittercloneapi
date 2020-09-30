from django.shortcuts import render
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from tweets.models import Tweets
from tweets.serializers import TweetSerializer
# Create your views here.


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def tweet(request):
    tweets = Tweets.objects.all()
    serializer = TweetSerializer(tweets, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def edit_tweet(request, pk):
    try:
        tweet = Tweets.objects.get(pk=pk)
    except Tweets.DoesNotExist:
        return Response('Tweet is not found', status=status.HTTP_404_NOT_FOUND)
    if request.method == 'PUT':
        if tweet.tweep == request.user:
            serializer = TweetSerializer(tweet, data=request.data)
            if serializer.is_valid():
                serializer.save(tweep=request.user)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response('You cannot edit this post because you were not the tweep that created it')
    return Response(serializer.errors, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_tweet(request, pk):
    try:
        tweet = Tweets.objects.get(pk=pk)
    except Tweets.DoesNotExist:
        return Response('The Tweet you are trying to delete cannot be found', status=status.HTTP_404_NOT_FOUND)
    if request.method == 'DELETE':
        tweet.delete()
        return Response('Delete successful')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_tweet(request):
    user = request.user
    if request.method == 'POST':
        serializer = TweetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(tweep=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(serializer.errors, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET'])
def tweet_detail(request, pk):
    try:
        tweet = Tweets.objects.get(pk=pk)
    except Tweets.DoesNotExist:
        return Response('The tweet you are trying to fetch does not exist', status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        serializer = TweetSerializer(tweet)
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def like(request, pk):
    tweet = Tweets.objects.get(pk=pk)
    # serializer = TweetSerializer(data=request.data)
    if not request.user in tweet.liker.all():
        tweet.likes += 1
        tweet.liker.add(request.user)
        tweet.save()
        TweetSerializer(tweet)
        return Response('You have liked this post')
    return Response('You cannot like this post more than once')
    # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def unlike(request, pk):
    tweet = Tweets.objects.get(pk=pk)
    if request.user in tweet.liker.all():
        tweet.likes -= 1
        tweet.liker.remove(request.user)
        tweet.save()
        return Response('You have unlike this post')
    return Response('You cannot unlike this post more than once')