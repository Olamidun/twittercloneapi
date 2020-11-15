from django.urls import path

from accounts import views

app_name = "accounts"

urlpatterns = [
    path('register', views.registration, name="register"),
    path('email_verification', views.verify_email, name="verify_email"),
    path('login', views.login, name="login"), 
    path('profile/', views.profile, name="profile"),
    path('profile/<str:username>/edit', views.update_profile, name="update-profile"),
    path('search', views.SearchView.as_view(), name="search"),
    path('<username>/follow/', views.follow, name="follow"),
]