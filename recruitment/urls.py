from django.urls import path

from . import views

app_name = "recruitment"

urlpatterns = [
    path("jobs/", views.JobListView.as_view(), name="jobs"),
    path("jobs/new/", views.JobCreateView.as_view(), name="job_create"),
    path("jobs/<int:pk>/", views.JobDetailView.as_view(), name="job_detail"),
    path("applicants/", views.ApplicantListView.as_view(), name="applicants"),
    path("applications/", views.ApplicationListView.as_view(), name="applications"),
    path(
        "applications/<int:pk>/stage/",
        views.update_application_stage,
        name="update_stage",
    ),
]
