from rest_framework import serializers
from tweets.models import Tweets, Comments


class TweetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tweets
        fields = ['id', 'texts', 'date_posted', 'tweep']

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comments
        