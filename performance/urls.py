from django.urls import path

from . import views

app_name = "performance"

urlpatterns = [
    path("cycles/", views.ReviewCycleListView.as_view(), name="cycles"),
    path("goals/", views.GoalListView.as_view(), name="goals"),
    path("goals/new/", views.GoalCreateView.as_view(), name="goal_create"),
    path("reviews/", views.ReviewListView.as_view(), name="reviews"),
]
