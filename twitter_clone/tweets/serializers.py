from rest_framework import serializers
from tweets.models import Tweets, Comments


class TweetSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField('get_tweep_username')
    class Meta:
        model = Tweets
        fields = ['texts', 'images', 'date_posted', 'username']
        extra_kwargs = {
            "images": {
                "required": False
            }
        }

    def get_tweep_username(self, tweets):
        username = tweets.tweep.username
        return username

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comments
        fields = '__all__'