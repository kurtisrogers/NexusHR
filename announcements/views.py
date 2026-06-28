from django.contrib import messages
from django.urls import reverse
from django.views.generic import CreateView, ListView

from accounts.mixins import HRStaffRequiredMixin
from announcements.forms import AnnouncementForm
from announcements.models import Announcement, PolicyDocument
from tenancy.mixins import TenantUserRequiredMixin
from tenancy.scoping import get_scope


class AnnouncementListView(TenantUserRequiredMixin, ListView):
    model = Announcement
    template_name = "announcements/announcement_list.html"
    context_object_name = "announcements"
    paginate_by = 10

    def get_queryset(self):
        scope = get_scope(self.request)
        qs = scope.announcements().filter(is_active=True).select_related("author", "department")
        return scope.filter_announcements(qs, self.request.user)


class AnnouncementCreateView(HRStaffRequiredMixin, TenantUserRequiredMixin, CreateView):
    model = Announcement
    form_class = AnnouncementForm
    template_name = "announcements/announcement_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["tenant"] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, "Announcement published.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("announcements:list")


class PolicyListView(TenantUserRequiredMixin, ListView):
    model = PolicyDocument
    template_name = "announcements/policy_list.html"
    context_object_name = "policies"

    def get_queryset(self):
        return get_scope(self.request).policy_documents().filter(is_active=True)
