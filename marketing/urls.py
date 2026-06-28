from django.urls import path

from marketing import views

app_name = "marketing"

urlpatterns = [
    path("", views.LandingView.as_view(), name="landing"),
    path("pricing/", views.PricingView.as_view(), name="pricing"),
    path("terms/", views.TermsView.as_view(), name="terms"),
    path("privacy/", views.PrivacyView.as_view(), name="privacy"),
    path("signup/", views.SignupView.as_view(), name="signup"),
    path("signup/success/", views.SignupSuccessView.as_view(), name="signup_success"),
]
