from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.LoginPageView.as_view(), name="login"),
    path("logout/", views.LogoutPageView.as_view(), name="logout"),
    path("users/", views.UserListView.as_view(), name="users"),
    path("password-reset/", views.TenantPasswordResetView.as_view(), name="password_reset"),
    path(
        "password-reset/done/",
        views.TenantPasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "password-reset/<uidb64>/<token>/",
        views.TenantPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "password-reset/complete/",
        views.TenantPasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
]
