from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.registerPage, name="register"),
    path("login/", views.loginPage, name="login" ),
    path("logout/", views.logoutPage, name="logout"),
    path("create-user/", views.UserView.as_view(), name="create-user"),
    path("get-user/", views.UserLoginView.as_view(), name="get-user"),
    path("login-user/", views.UserLoginView.as_view(), name="login-user"),
]