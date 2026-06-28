from django import forms

from recruitment.models import Applicant, Application, Interview, JobPosting
from tenancy.scoping import TenantScope


class JobPostingForm(forms.ModelForm):
    class Meta:
        model = JobPosting
        fields = [
            "title",
            "department",
            "job_title",
            "description",
            "requirements",
            "location",
            "employment_type",
            "salary_min",
            "salary_max",
            "status",
            "openings",
            "closing_date",
        ]
        widgets = {"closing_date": forms.DateInput(attrs={"type": "date"})}

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            scope = TenantScope(tenant)
            self.fields["department"].queryset = scope.departments()
            self.fields["job_title"].queryset = scope.job_titles()


class ApplicantForm(forms.ModelForm):
    class Meta:
        model = Applicant
        fields = ["first_name", "last_name", "email", "phone", "resume", "linkedin", "source"]


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ["job", "applicant", "stage", "cover_letter", "rating", "notes"]

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tenant:
            scope = TenantScope(tenant)
            self.fields["job"].queryset = scope.job_postings()
            self.fields["applicant"].queryset = scope.applicants()


class InterviewForm(forms.ModelForm):
    class Meta:
        model = Interview
        fields = [
            "application",
            "interviewer",
            "scheduled_at",
            "duration_minutes",
            "location",
            "notes",
            "feedback",
            "rating",
            "completed",
        ]
        widgets = {"scheduled_at": forms.DateTimeInput(attrs={"type": "datetime-local"})}
