from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView

from accounts.mixins import RecruiterRequiredMixin
from billing.entitlements import Feature
from recruitment.forms import JobPostingForm
from recruitment.models import Applicant, Application, ApplicationStage, JobPosting
from tenancy.mixins import FeatureRequiredMixin, TenantUserRequiredMixin
from tenancy.scoping import get_scope


class JobListView(FeatureRequiredMixin, TenantUserRequiredMixin, ListView):
    required_feature = Feature.RECRUITMENT
    model = JobPosting
    template_name = "recruitment/job_list.html"
    context_object_name = "jobs"
    paginate_by = 20

    def get_queryset(self):
        scope = get_scope(self.request)
        qs = scope.job_postings().select_related("department", "posted_by")
        if not self.request.user.can_recruit:
            qs = qs.filter(status="open")
        return qs


class JobDetailView(FeatureRequiredMixin, TenantUserRequiredMixin, DetailView):
    required_feature = Feature.RECRUITMENT
    model = JobPosting
    template_name = "recruitment/job_detail.html"
    context_object_name = "job"

    def get_queryset(self):
        return get_scope(self.request).job_postings()


class JobCreateView(
    FeatureRequiredMixin, RecruiterRequiredMixin, TenantUserRequiredMixin, CreateView
):
    required_feature = Feature.RECRUITMENT
    model = JobPosting
    form_class = JobPostingForm
    template_name = "recruitment/job_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["tenant"] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        form.instance.posted_by = self.request.user
        messages.success(self.request, "Job posting created.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("recruitment:job_detail", kwargs={"pk": self.object.pk})


class ApplicantListView(
    FeatureRequiredMixin, RecruiterRequiredMixin, TenantUserRequiredMixin, ListView
):
    required_feature = Feature.RECRUITMENT
    model = Applicant
    template_name = "recruitment/applicant_list.html"
    context_object_name = "applicants"
    paginate_by = 20

    def get_queryset(self):
        return get_scope(self.request).applicants()


class ApplicationListView(
    FeatureRequiredMixin, RecruiterRequiredMixin, TenantUserRequiredMixin, ListView
):
    required_feature = Feature.RECRUITMENT
    model = Application
    template_name = "recruitment/application_list.html"
    context_object_name = "applications"
    paginate_by = 20

    def get_queryset(self):
        scope = get_scope(self.request)
        qs = scope.applications().select_related("job", "applicant")
        stage = self.request.GET.get("stage")
        if stage:
            qs = qs.filter(stage=stage)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["stages"] = ApplicationStage.choices
        ctx["current_stage"] = self.request.GET.get("stage", "")
        return ctx


def update_application_stage(request, pk):
    if not request.user.is_authenticated:
        return redirect("accounts:login")
    scope = get_scope(request)
    application = get_object_or_404(scope.applications(), pk=pk)
    if request.method == "POST" and request.user.can_recruit:
        stage = request.POST.get("stage")
        if stage in dict(ApplicationStage.choices):
            application.stage = stage
            application.save()
            messages.success(request, f"Moved to {application.get_stage_display()}.")
        if request.htmx:
            return render(
                request,
                "recruitment/partials/application_row.html",
                {"app": application, "stages": ApplicationStage.choices},
            )
    return redirect("recruitment:applications")
