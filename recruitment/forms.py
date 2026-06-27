from django import forms

from recruitment.models import Applicant, Application, Interview, JobPosting


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


class ApplicantForm(forms.ModelForm):
    class Meta:
        model = Applicant
        fields = ["first_name", "last_name", "email", "phone", "resume", "linkedin", "source"]


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ["job", "applicant", "stage", "cover_letter", "rating", "notes"]


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
