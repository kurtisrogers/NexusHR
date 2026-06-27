from django import forms

from performance.models import Goal, PerformanceReview, ReviewCycle


class ReviewCycleForm(forms.ModelForm):
    class Meta:
        model = ReviewCycle
        fields = ["name", "description", "start_date", "end_date", "status"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }


class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ["title", "description", "target_date", "progress", "status", "weight", "cycle"]
        widgets = {"target_date": forms.DateInput(attrs={"type": "date"})}


class PerformanceReviewForm(forms.ModelForm):
    class Meta:
        model = PerformanceReview
        fields = [
            "self_rating",
            "self_comments",
            "manager_rating",
            "manager_comments",
            "overall_rating",
            "status",
        ]
