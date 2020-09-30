from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


# Create your models here.

class Tweets(models.Model):
    texts = models.TextField()
    images = models.FileField(upload_to='images', blank=True, null=True)
    date_posted = models.DateTimeField(auto_now_add=True)
    tweep = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    likes = models.IntegerField(default=0)
    liker = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='user_like')
    # link = models.URLField()

    class Meta:
        # verbose_name = _('my thing')
        verbose_name_plural = _('Tweets')

    def __str__(self):
        return f"{self.tweep.username}'s tweet"


class Comments(models.Model):
    tweet = models.ForeignKey(Tweets, on_delete=models.CASCADE)
    comment = models.TextField(null=True, blank=True)
    images = models.FileField(upload_to="comment_images", null=True, blank=True)
    date_commented = models.DateTimeField(auto_now_add=True)
    commenter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        # verbose_name = _('my thing')
        verbose_name_plural = _('Comments')

    def __str__(self):
        return f"{self.commenter.username}'s comments"