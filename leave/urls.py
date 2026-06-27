from django.urls import path

from . import views

app_name = "leave"

urlpatterns = [
    path("", views.LeaveRequestListView.as_view(), name="list"),
    path("new/", views.LeaveRequestCreateView.as_view(), name="create"),
    path("balances/", views.leave_balances, name="balances"),
    path("<int:pk>/approve/", views.approve_leave, name="approve"),
]
