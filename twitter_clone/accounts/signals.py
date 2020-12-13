from django.db.models.signals import post_save
from accounts.models import Account
from tweets.models import Follow, Tweets, Stream
from django.db import transaction
from django.dispatch import receiver
from accounts.models import Profile
from django.core.exceptions import ObjectDoesNotExist


@receiver(post_save, sender=Account)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=Account)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()


@receiver(post_save, sender=Account)
def follow_superuser(sender, instance, created, **kwargs):
    following = Account.objects.get(email='opeoluwakolapo@yahoo.com')
    if created:
        Follow.objects.create(followers=instance, following=following)
        tweets = Tweets.objects.all().filter(tweep=following)

        with transaction.atomic():
                for tweet in tweets:
                    stream = Stream(tweet=tweet, user=instance, following=following)
                    stream.save()