from django.db import models
from django.contrib.auth.models import User
# Create your models here.


# class UserProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     date_joined = models.DateTimeField(auto_now_add=True)
#     profile_image = models.ImageField(upload_to="profile_picture")
#     followers = models.ManyToManyField(User, related_name='user_followers')
#     following = models.ManyToManyField(User, related_name='user_following')
#     number_of_followers = models.BigIntegerField(default=0)
#     number_of_followings = models.BigIntegerField(default=0)
#     def __str__(self):
#         return self.user
