from django.contrib import messages
from django.db.models import Q
from django.urls import reverse
from django.views.generic import CreateView, ListView

from accounts.mixins import HRStaffRequiredMixin
from billing.entitlements import Feature
from performance.forms import GoalForm
from performance.models import Goal, PerformanceReview, ReviewCycle
from tenancy.mixins import FeatureRequiredMixin, TenantUserRequiredMixin
from tenancy.scoping import get_scope


class ReviewCycleListView(FeatureRequiredMixin, HRStaffRequiredMixin, TenantUserRequiredMixin, ListView):
    required_feature = Feature.PERFORMANCE
    model = ReviewCycle
    template_name = "performance/cycle_list.html"
    context_object_name = "cycles"

    def get_queryset(self):
        return get_scope(self.request).review_cycles()


class GoalListView(FeatureRequiredMixin, TenantUserRequiredMixin, ListView):
    required_feature = Feature.PERFORMANCE
    model = Goal
    template_name = "performance/goal_list.html"
    context_object_name = "goals"

    def get_queryset(self):
        scope = get_scope(self.request)
        qs = scope.goals().select_related("employee__user", "cycle")
        return scope.filter_goals(qs, self.request.user)


class GoalCreateView(FeatureRequiredMixin, TenantUserRequiredMixin, CreateView):
    required_feature = Feature.PERFORMANCE
    model = Goal
    form_class = GoalForm
    template_name = "performance/goal_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["tenant"] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        form.instance.employee = self.request.user.employee_profile
        messages.success(self.request, "Goal created.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("performance:goals")


class ReviewListView(FeatureRequiredMixin, TenantUserRequiredMixin, ListView):
    required_feature = Feature.PERFORMANCE
    model = PerformanceReview
    template_name = "performance/review_list.html"
    context_object_name = "reviews"

    def get_queryset(self):
        scope = get_scope(self.request)
        qs = scope.performance_reviews().select_related("employee__user", "cycle", "reviewer")
        return scope.filter_reviews(qs, self.request.user)
