from django.test import Client, TestCase
from django.urls import reverse

from announcements.models import Announcement, PolicyDocument
from hrms.test_utils import create_hr_setup


class AnnouncementViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.data = create_hr_setup()
        Announcement.objects.create(
            title="Company-wide Update",
            content="All hands next Friday.",
            author=self.data["hr_admin"],
            is_pinned=True,
        )
        Announcement.objects.create(
            title="Engineering Only",
            content="Sprint planning moved.",
            author=self.data["hr_admin"],
            department=self.data["department"],
        )
        PolicyDocument.objects.create(
            title="Remote Work Policy",
            category="Workplace",
            content="Work from home up to 3 days.",
            effective_date="2024-01-01",
        )

    def test_employee_sees_company_and_dept_announcements(self):
        self.client.login(username="emp", password="testpass123")
        response = self.client.get(reverse("announcements:list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Company-wide Update")
        self.assertContains(response, "Engineering Only")

    def test_hr_can_create_announcement(self):
        self.client.login(username="hr_admin", password="testpass123")
        response = self.client.get(reverse("announcements:create"))
        self.assertEqual(response.status_code, 200)

    def test_policies_list(self):
        self.client.login(username="emp", password="testpass123")
        response = self.client.get(reverse("announcements:policies"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Remote Work Policy")
