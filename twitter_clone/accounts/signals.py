from django.db.models.signals import post_save
from accounts.models import Account
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