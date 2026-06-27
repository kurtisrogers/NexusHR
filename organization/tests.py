from django.test import Client, TestCase
from django.urls import reverse

from hrms.test_utils import create_hr_setup


class OrganizationViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.data = create_hr_setup()

    def test_departments_list_for_hr(self):
        self.client.login(username="hr_admin", password="testpass123")
        response = self.client.get(reverse("organization:departments"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Engineering")

    def test_locations_list_for_hr(self):
        self.client.login(username="hr_admin", password="testpass123")
        response = self.client.get(reverse("organization:locations"))
        self.assertEqual(response.status_code, 200)

    def test_job_titles_list_for_hr(self):
        self.client.login(username="hr_admin", password="testpass123")
        response = self.client.get(reverse("organization:job_titles"))
        self.assertEqual(response.status_code, 200)

    def test_department_create_form(self):
        self.client.login(username="hr_admin", password="testpass123")
        response = self.client.get(reverse("organization:department_create"))
        self.assertEqual(response.status_code, 200)
