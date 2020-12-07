from django.db import models
from django.conf import settings
import uuid
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from cloudinary.models import CloudinaryField


# Create your models here.

class TweetFile(models.Model):
    tweep =  models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    media = CloudinaryField('images')

    def __str__(self):
        return f"{self.tweep.username}'s tweet images"
    

class Tweets(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    texts = models.TextField(null=True, blank=True)
    file_content = models.ManyToManyField(TweetFile, related_name='file_content', blank=True, null=True)
    date_posted = models.DateTimeField(auto_now_add=True)
    tweep = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    likes = models.PositiveIntegerField(default=0)
    liker = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='user_like')
    # link = models.URLField()

    class Meta:
        # verbose_name = _('my thing')
        verbose_name_plural = _('Tweets')

    def __str__(self):
        return f"{self.texts}"


class CommentFile(models.Model):
    tweep =  models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment_media = CloudinaryField('comment_images')

    def __str__(self):
        return f"{self.tweep.username}'s comment images"

class Comments(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tweet = models.ForeignKey(Tweets, on_delete=models.CASCADE)
    comment = models.TextField(null=True, blank=True)
    comment_files = models.ManyToManyField(CommentFile, related_name='comment_file_content', blank=True, null=True)
    date_commented = models.DateTimeField(auto_now_add=True)
    commenter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment_likes = models.PositiveIntegerField(default=0)
    comment_liker = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='comment_liker')

    class Meta:
        # verbose_name = _('my thing')
        verbose_name_plural = _('Comments')

    def __str__(self):
        return f"{self.commenter.username}'s comments"


class Follow(models.Model):
    followers = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='follower')
    following = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='following')

    def __str__(self):
        return f"{self.followers.username} is following {self.following.username}"

class Stream(models.Model):
    following = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='stream_follower')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tweet = models.ForeignKey(Tweets, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.following.username}'s tweet showing on {self.user.username}'s timeline"

    def add_post(sender, instance, *args, **kwargs):
        tweet = instance
        user = tweet.tweep
        followers = Follow.objects.all().filter(following=user)
        for follower in followers:
            stream = Stream(tweet=tweet, user=follower.followers, date=tweet.date_posted, following=user)
            stream.save()

post_save.connect(Stream.add_post, sender=Tweets)