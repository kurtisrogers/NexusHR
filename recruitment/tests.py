from django.test import Client, TestCase
from django.urls import reverse

from accounts.models import UserRole
from hrms.test_utils import create_application, create_hr_setup, create_job_posting, create_user
from recruitment.models import ApplicationStage, JobStatus


class RecruitmentViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.data = create_hr_setup()
        self.recruiter = create_user("recruiter", UserRole.RECRUITER)
        self.job = create_job_posting(
            department=self.data["department"],
            posted_by=self.recruiter,
            status=JobStatus.OPEN,
        )
        self.application = create_application(job=self.job, stage=ApplicationStage.SCREENING)

    def test_employee_sees_open_jobs(self):
        self.client.login(username="emp", password="testpass123")
        response = self.client.get(reverse("recruitment:jobs"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Software Engineer")

    def test_recruiter_can_create_job(self):
        self.client.login(username="recruiter", password="testpass123")
        response = self.client.get(reverse("recruitment:job_create"))
        self.assertEqual(response.status_code, 200)

    def test_employee_cannot_create_job(self):
        self.client.login(username="emp", password="testpass123")
        response = self.client.get(reverse("recruitment:job_create"))
        self.assertEqual(response.status_code, 403)

    def test_update_application_stage(self):
        self.client.login(username="recruiter", password="testpass123")
        response = self.client.post(
            reverse("recruitment:update_stage", kwargs={"pk": self.application.pk}),
            {"stage": ApplicationStage.INTERVIEW},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.application.refresh_from_db()
        self.assertEqual(self.application.stage, ApplicationStage.INTERVIEW)

    def test_job_detail_page(self):
        self.client.login(username="emp", password="testpass123")
        response = self.client.get(
            reverse("recruitment:job_detail", kwargs={"pk": self.job.pk}),
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Build great software")
