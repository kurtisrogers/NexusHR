from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.LoginPageView.as_view(), name="login"),
    path("logout/", views.LogoutPageView.as_view(), name="logout"),
    path("users/", views.UserListView.as_view(), name="users"),
]
