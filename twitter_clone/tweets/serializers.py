from rest_framework import serializers
from tweets.models import Tweets, Comments


class TweetSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField('get_tweep_username')
    likes = serializers.SerializerMethodField('get_tweet_likes')
    liker = serializers.StringRelatedField(many=True)

    class Meta:
        model = Tweets
        fields = ['texts', 'images', 'date_posted', 'username', 'likes', 'liker']
        extra_kwargs = {
            "images": {
                "required": False,
            }
        }
    # function that returns the owner of a tweet
    def get_tweep_username(self, tweets):
        username = tweets.tweep.username
        return username

    # function that returns the number of likes a tweet has
    def get_tweet_likes(self, tweets):
        likes = tweets.likes
        return likes


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comments
        fields = '__all__'