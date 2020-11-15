from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from tweets.models import Tweets
# Create your models here.

class AccountManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        if username is None:
            raise TypeError("Users shold have a username")
        if email is None:
            raise TypeError("Users shold have an email")
        user = self.model(
            username=username,
            email=self.normalize_email(email)
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password):
        user = self.create_user(username, email, password)
        user.is_superuser = True
        user.is_staff = True
        user.is_admin = True
        user.is_verified = True
        user.save(using=self._db)
        return user



class Account(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    is_verified = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = AccountManager()

    def __str__(self):
        return self.username


    def token(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }



class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile", null=True, blank=True)
    bio = models.CharField(max_length=255)
    location = models.CharField(max_length=100)
    Website = models.URLField()
    profile_image = models.ImageField(upload_to="profile_picture")

    def __str__(self):
        return f"{self.user.username}'s Profile"
