from django.urls import path

from . import views

app_name = "announcements"

urlpatterns = [
    path("", views.AnnouncementListView.as_view(), name="list"),
    path("new/", views.AnnouncementCreateView.as_view(), name="create"),
    path("policies/", views.PolicyListView.as_view(), name="policies"),
]
