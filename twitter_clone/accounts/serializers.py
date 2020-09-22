# from accounts.models import UserProfile
from rest_framework import serializers
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}


    def validate(self, data):
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({'email': {'email already exist'}})
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError({'username': {'username already exist'}})
        return super().validate(data)


    def create(self, validated_data):
        # user = User(
        #     email=validated_data['email'],
        #     username=validated_data['username'],
        # )
        # user.set_password(validated_data['password'])
        # user.save()
        # Token.objects.create(user=user)
        return User.objects.create_user(username=validated_data['username'], email=validated_data['email'], password=validated_data['password'])
    
    # def validate_email(self, data):
    #     if User.objects.filter(email__iexact=data['email']).exists():
    #         raise serializers.ValidationError({'email': 'Email already exists'})
    #     return data

    # def save(self):
    #     user = User(
    #         username=self.validated_data.get('username'),
    #         email=self.validated_data.get('email')
    #     )
    #     user.set_password(self.validated_data.get('password'))
    #     user.save()
    #     return



class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(read_only=True)
    date_joined = serializers.DateTimeField(read_only=True)
    active = serializers.BooleanField(read_only=True)
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'date_joined', 'active']

    def validate(self, data):
        username = data['username']
        password = data['password']
        user = authenticate(username=username, password=password)
        
        if not user:
            raise serializers.ValidationError({"error": "Invalid login details, try again"})
        return {
            "email": user.email,
            "username": user.username,
            "date_joined": user.date_joined,
            "active": user.is_active
        }
        # print(super().validate(data))
        # return super().validate(data)


# class UserProfileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UserProfile
#         fields = ['user', 'date_joined', 'profile_image', 'number_of_followers', 'number_of_followings']