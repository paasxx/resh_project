from django.urls import path

from . import views

urlpatterns = [

    # FrontEnd endpoints
    path("", views.home, name="home"),
    path("register/", views.registerPage, name="register"),
    path("login/", views.loginPage, name="login" ),
    path("logout/", views.logoutPage, name="logout"),
    path("updatePassword/", views.updatePasswordPage, name="updatePassword"),
    path("delete/", views.deletePage, name="delete"),
    
    # API endpoints
    path("api-create-user/", views.RegisterView.as_view(), name="create-user"),
    path("api-get-user/", views.UserView.as_view(), name="get-user"),
    path("api-login-user/", views.LoginView.as_view(), name="login-user"),
    path("api-logout-user/", views.LogoutView.as_view(), name="logout-user"),
    path("api-update-user/", views.UpdatePasswordUserView.as_view(), name="update-password-user"),
    path("api-delete-user/", views.DeleteUserView.as_view(), name="delete-user"),
   
]
