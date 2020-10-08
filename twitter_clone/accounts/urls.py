from django.urls import path

from accounts import views

app_name = "accounts"

urlpatterns = [
    path('register', views.registration, name="register"),
    path('email_verification', views.verify_email, name="verify_email"),
    path('login', views.login, name="login"), 
    path('search', views.SearchView.as_view(), name="search")
]