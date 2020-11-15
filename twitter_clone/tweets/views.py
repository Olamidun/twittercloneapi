from django.shortcuts import render
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from tweets.models import Tweets, Comments, Stream
from tweets.serializers import TweetSerializer, CommentSerializer
# Create your views here.


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def tweet(request):
    streams = Stream.objects.filter(user=request.user)

    group_ids = []
    for stream in streams:
        group_ids.append(stream.tweet_id)
    print(group_ids)
    tweets = Tweets.objects.filter(id__in=group_ids).all()
    
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
        if tweet.tweep == request.user:
            tweet.delete()
            return Response('Delete successful')
        return Response('You cannot delete this post because you are not the author')
    return Response('Bad Http request', status=status.HTTP_405_METHOD_NOT_ALLOWED)


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


@api_view(['PATCH'])
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


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def unlike(request, pk):
    tweet = Tweets.objects.get(pk=pk)
    if request.user in tweet.liker.all():
        tweet.likes -= 1
        tweet.liker.remove(request.user)
        tweet.save()
        return Response('You have unliked this post')
    return Response('You cannot unlike this post more than once')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def comments_list(request, pk):
    tweet = Tweets.objects.get(pk=pk)
    comments = Comments.objects.filter(tweet=tweet)
    serializer = CommentSerializer(comments, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_comment(request, pk):
    tweet = Tweets.objects.get(pk=pk)
    user = request.user
    if request.method == 'POST':
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(commenter=user, tweet=tweet)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(serializer.errors, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_comment(request, pk):
    try:
        comment = Comments.objects.get(pk=pk)
    except comment.DoesNotExist:
        return Response('The comment you are looking for does not exist!')
    if request.method == 'DELETE':
        if request.user == comment.commenter:
            comment.delete()
            return Response('This comment has been deleted sccessfully', status=status.HTTP_200_OK)
        else:
            return Response('You cannot delete this comment as you are not the commenter', status=status.HTTP_401_UNAUTHORIZED)
    return Response('Bad')


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def like_comment(request, pk):
    try:
        comment = Comments.objects.get(pk=pk)
    # serializer = TweetSerializer(data=request.data)
    except comment.DoesNotExist:
        return Response('The comment you are looking for does not exist!')
    if request.method == "PATCH":
        if not request.user in comment.comment_liker.all():
            comment.comment_likes += 1
            comment.comment_liker.add(request.user)
            comment.save()
            return Response('You have liked this comment')
        return Response('You cannot like this comment more than once')
    return Response('Bad request', status=status.HTTP_405_METHOD_NOT_ALLOWED)
    


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def unlike_comment(request, pk):
    try:
        comment = Comments.objects.get(pk=pk)
    except comment.DoesNotExist:
        return Response('The comment you are looking for does not exist!')
    if request.method == 'PATCH':
        if request.user in comment.comment_liker.all():
            comment.comment_likes -= 1
            comment.comment_liker.remove(request.user)
            comment.save()
            return Response('You have unliked this post')
        return Response('You cannot unlike this post more than once')
    return Response('Bad request', status=status.HTTP_405_METHOD_NOT_ALLOWED)
