from django.urls import path

from billing import views

app_name = "billing"

urlpatterns = [
    path("", views.BillingSettingsView.as_view(), name="settings"),
    path("upgrade/<slug:slug>/", views.UpgradePlanView.as_view(), name="upgrade"),
    path("portal/", views.CustomerPortalView.as_view(), name="portal"),
]
