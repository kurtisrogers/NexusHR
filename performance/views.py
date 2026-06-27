from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import CreateView, ListView, UpdateView

from accounts.mixins import HRStaffRequiredMixin, ManagerRequiredMixin
from performance.forms import GoalForm, PerformanceReviewForm, ReviewCycleForm
from performance.models import Goal, PerformanceReview, ReviewCycle


class ReviewCycleListView(HRStaffRequiredMixin, ListView):
    model = ReviewCycle
    template_name = "performance/cycle_list.html"
    context_object_name = "cycles"


class GoalListView(LoginRequiredMixin, ListView):
    model = Goal
    template_name = "performance/goal_list.html"
    context_object_name = "goals"

    def get_queryset(self):
        qs = Goal.objects.select_related("employee__user", "cycle")
        if self.request.user.is_hr_staff:
            return qs
        if hasattr(self.request.user, "employee_profile"):
            profile = self.request.user.employee_profile
            if self.request.user.is_manager_or_above:
                from django.db.models import Q

                return qs.filter(
                    Q(employee=profile)
                    | Q(employee__manager=profile)
                )
            return qs.filter(employee=profile)
        return qs.none()


class GoalCreateView(LoginRequiredMixin, CreateView):
    model = Goal
    form_class = GoalForm
    template_name = "performance/goal_form.html"

    def form_valid(self, form):
        form.instance.employee = self.request.user.employee_profile
        messages.success(self.request, "Goal created.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("performance:goals")


class ReviewListView(LoginRequiredMixin, ListView):
    model = PerformanceReview
    template_name = "performance/review_list.html"
    context_object_name = "reviews"

    def get_queryset(self):
        qs = PerformanceReview.objects.select_related(
            "employee__user", "cycle", "reviewer"
        )
        if self.request.user.is_hr_staff:
            return qs
        if hasattr(self.request.user, "employee_profile"):
            profile = self.request.user.employee_profile
            from django.db.models import Q

            return qs.filter(
                Q(employee=profile) | Q(reviewer=self.request.user)
            )
        return qs.none()
