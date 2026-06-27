from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView

from accounts.mixins import RecruiterRequiredMixin
from recruitment.forms import JobPostingForm
from recruitment.models import Applicant, Application, ApplicationStage, JobPosting


class JobListView(LoginRequiredMixin, ListView):
    model = JobPosting
    template_name = "recruitment/job_list.html"
    context_object_name = "jobs"
    paginate_by = 20

    def get_queryset(self):
        qs = JobPosting.objects.select_related("department", "posted_by")
        if not self.request.user.can_recruit:
            qs = qs.filter(status="open")
        return qs


class JobDetailView(LoginRequiredMixin, DetailView):
    model = JobPosting
    template_name = "recruitment/job_detail.html"
    context_object_name = "job"


class JobCreateView(RecruiterRequiredMixin, CreateView):
    model = JobPosting
    form_class = JobPostingForm
    template_name = "recruitment/job_form.html"

    def form_valid(self, form):
        form.instance.posted_by = self.request.user
        messages.success(self.request, "Job posting created.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("recruitment:job_detail", kwargs={"pk": self.object.pk})


class ApplicantListView(RecruiterRequiredMixin, ListView):
    model = Applicant
    template_name = "recruitment/applicant_list.html"
    context_object_name = "applicants"
    paginate_by = 20


class ApplicationListView(RecruiterRequiredMixin, ListView):
    model = Application
    template_name = "recruitment/application_list.html"
    context_object_name = "applications"
    paginate_by = 20

    def get_queryset(self):
        qs = Application.objects.select_related("job", "applicant")
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
    application = get_object_or_404(Application, pk=pk)
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
