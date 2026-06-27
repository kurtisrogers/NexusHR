from django.urls import path

from . import views

app_name = "employees"

urlpatterns = [
    path("", views.EmployeeListView.as_view(), name="list"),
    path("new/", views.EmployeeCreateView.as_view(), name="create"),
    path("profile/", views.EmployeeProfileUpdateView.as_view(), name="profile"),
    path("<int:pk>/", views.EmployeeDetailView.as_view(), name="detail"),
    path("<int:pk>/documents/", views.upload_document, name="upload_document"),
]
