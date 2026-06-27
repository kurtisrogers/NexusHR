from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from attendance.models import AttendanceRecord, AttendanceStatus
from hrms.test_utils import create_hr_setup


class AttendanceViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.data = create_hr_setup()

    def test_clock_in_creates_record(self):
        self.client.login(username="emp", password="testpass123")
        response = self.client.post(reverse("attendance:clock_in"))
        self.assertEqual(response.status_code, 302)
        today = timezone.localdate()
        record = AttendanceRecord.objects.get(
            employee=self.data["employee"],
            date=today,
        )
        self.assertIsNotNone(record.clock_in)
        self.assertEqual(record.status, AttendanceStatus.PRESENT)

    def test_clock_out_updates_record(self):
        self.client.login(username="emp", password="testpass123")
        self.client.post(reverse("attendance:clock_in"))
        response = self.client.post(reverse("attendance:clock_out"))
        self.assertEqual(response.status_code, 302)
        today = timezone.localdate()
        record = AttendanceRecord.objects.get(
            employee=self.data["employee"],
            date=today,
        )
        self.assertIsNotNone(record.clock_out)
        self.assertIsNotNone(record.clock_in)

    def test_clock_in_htmx_returns_partial(self):
        self.client.login(username="emp", password="testpass123")
        response = self.client.post(
            reverse("attendance:clock_in"),
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Clock In")

    def test_attendance_list_requires_login(self):
        response = self.client.get(reverse("attendance:list"))
        self.assertEqual(response.status_code, 302)
