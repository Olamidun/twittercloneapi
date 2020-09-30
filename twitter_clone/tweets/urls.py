from django.urls import path
from tweets import views

app_name = 'tweets'

urlpatterns = [
    path('', views.tweet, name="tweets"),
    path('tweet/<int:pk>', views.tweet_detail, name="tweet-detail"),
    path('edit/<int:pk>', views.edit_tweet, name="edit-tweet"), 
    path('create_tweet', views.create_tweet, name="create-tweet"),
    path('delete_tweet/<int:pk>', views.delete_tweet, name="delete-tweet"),
    path('like-tweet/<int:pk>', views.like, name="like-tweet"),
    path('unlike-tweet/<int:pk>', views.unlike, name="unlike-tweet")
]