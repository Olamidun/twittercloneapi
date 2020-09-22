from django.urls import path

from accounts import views

app_name = "account"

urlpatterns = [
    path('register', views.registration, name="register"),
    path('login', views.login, name="login")
]