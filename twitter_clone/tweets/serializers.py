from rest_framework import serializers
from tweets.models import Tweets, Comments


class TweetSerializer(serializers.ModelSerializer):
    tweep = serializers.SerializerMethodField('get_tweep_username')
    likes = serializers.SerializerMethodField('get_tweet_likes')
    liker = serializers.StringRelatedField(many=True)

    class Meta:
        model = Tweets
        fields = ['id','texts', 'images', 'date_posted', 'tweep', 'likes', 'liker']
        extra_kwargs = {
            "images": {
                "required": False,
            }
        }
    # function that returns the owner of a tweet
    def get_tweep_username(self, tweets):
        tweep = tweets.tweep.username
        return tweep

    # function that returns the number of likes a tweet has
    def get_tweet_likes(self, tweets):
        likes = tweets.likes
        return likes


class CommentSerializer(serializers.ModelSerializer):
    tweet = serializers.StringRelatedField(many=False)
    commenter = serializers.SerializerMethodField('get_commenter_username')
    comment_likes = serializers.SerializerMethodField('get_comment_likes')
    comment_liker = serializers.StringRelatedField(many=True)
    class Meta:
        model = Comments
        fields = ['tweet', 'comment', 'images', 'date_commented', 'commenter', 'comment_likes', 'comment_liker']
        extra_kwargs = {
            "images": {
                "required": False,
            }
        }

    
    # function that returns the owner of a comment
    def get_commenter_username(self, comments):
        commenter = comments.commenter.username
        return commenter

    # function that returns the number of likes a comment has
    def get_comment_likes(self, comments):
        comment_likes = comments.comment_likes
        return comment_likes