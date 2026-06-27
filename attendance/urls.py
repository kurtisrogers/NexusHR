from django.urls import path

from . import views

app_name = "attendance"

urlpatterns = [
    path("", views.AttendanceListView.as_view(), name="list"),
    path("clock-in/", views.clock_in, name="clock_in"),
    path("clock-out/", views.clock_out, name="clock_out"),
]
