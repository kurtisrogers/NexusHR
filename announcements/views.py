from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.urls import reverse
from django.views.generic import CreateView, ListView

from accounts.mixins import HRStaffRequiredMixin
from announcements.forms import AnnouncementForm
from announcements.models import Announcement, PolicyDocument


class AnnouncementListView(LoginRequiredMixin, ListView):
    model = Announcement
    template_name = "announcements/announcement_list.html"
    context_object_name = "announcements"
    paginate_by = 10

    def get_queryset(self):
        qs = Announcement.objects.filter(is_active=True).select_related("author", "department")
        user = self.request.user
        if user.is_hr_staff:
            return qs
        if hasattr(user, "employee_profile") and user.employee_profile.department:
            dept = user.employee_profile.department
            return qs.filter(Q(department__isnull=True) | Q(department=dept))
        return qs.filter(department__isnull=True)


class AnnouncementCreateView(HRStaffRequiredMixin, CreateView):
    model = Announcement
    form_class = AnnouncementForm
    template_name = "announcements/announcement_form.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, "Announcement published.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("announcements:list")


class PolicyListView(LoginRequiredMixin, ListView):
    model = PolicyDocument
    template_name = "announcements/policy_list.html"
    context_object_name = "policies"

    def get_queryset(self):
        return PolicyDocument.objects.filter(is_active=True)
