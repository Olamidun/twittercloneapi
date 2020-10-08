from django.urls import path
from tweets import views

app_name = 'tweets'

urlpatterns = [
    # TWEETS URLS
    path('', views.tweet, name="tweets"),
    path('tweet/<int:pk>', views.tweet_detail, name="tweet-detail"),
    path('edit/<int:pk>', views.edit_tweet, name="edit-tweet"), 
    path('create_tweet', views.create_tweet, name="create-tweet"),
    path('delete_tweet/<int:pk>', views.delete_tweet, name="delete-tweet"),
    path('like-tweet/<int:pk>', views.like, name="like-tweet"),
    path('unlike-tweet/<int:pk>', views.unlike, name="unlike-tweet"),

    # COMMENTS URLS
    path('tweet/<int:pk>/comments', views.comments_list, name="comment_lists"),
    path('tweet/<int:pk>/add_comment', views.add_comment, name="add_comment"),
    path('comment/<int:pk>', views.delete_comment, 
    name="delete-comment"),
    path('comment/<int:pk>/like_comment', views.like_comment, name="like-comment"),
    path('comment/<int:pk>/unlike_comment', views.unlike_comment, name="unlike-comment")
]