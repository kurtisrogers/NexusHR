from django.urls import path

from . import views

app_name = "organization"

urlpatterns = [
    path("departments/", views.DepartmentListView.as_view(), name="departments"),
    path("departments/new/", views.DepartmentCreateView.as_view(), name="department_create"),
    path("locations/", views.LocationListView.as_view(), name="locations"),
    path("job-titles/", views.JobTitleListView.as_view(), name="job_titles"),
]
