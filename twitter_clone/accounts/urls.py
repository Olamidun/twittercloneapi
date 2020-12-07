from django.urls import path

from accounts import views

app_name = "accounts"

urlpatterns = [
    path('register', views.registration, name="register"),
    path('email_verification', views.verify_email, name="verify_email"),
    path('login', views.login, name="login"), 
    path('logout', views.logout_view, name="logout"),
    path('request-password/', views.password_reset, name="reset"),
    path('password-reset/<uidb64>/<token>/', views.password_token_check, name="reset-password"),
    path('password-reset-complete', views.set_new_password, name="password-reset-complete"),
    path('profile/', views.profile, name="profile"),
    path('profile/<str:username>/edit', views.update_profile, name="update-profile"),
    path('search', views.SearchView.as_view(), name="search"),
    path('<str:username>/follow/', views.FollowView.as_view(), name="follow"),
    path('<str:username>/unfollow/', views.UnFollowView.as_view(), name="unfollow"),
    path('<str:username>/tweets', views.user_tweets, name="user_tweets"),
    path('<str:username>/media', views.user_media, name="user_media")
]