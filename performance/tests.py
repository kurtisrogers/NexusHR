from datetime import date, timedelta

from django.test import Client, TestCase
from django.urls import reverse

from hrms.test_utils import create_hr_setup
from performance.models import (
    Goal,
    GoalStatus,
    PerformanceReview,
    ReviewCycle,
    ReviewCycleStatus,
    ReviewStatus,
)


class PerformanceViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.data = create_hr_setup()
        self.cycle = ReviewCycle.objects.create(
            name="Q1 Review",
            start_date=date.today() - timedelta(days=30),
            end_date=date.today() + timedelta(days=30),
            status=ReviewCycleStatus.ACTIVE,
        )
        Goal.objects.create(
            employee=self.data["employee"],
            cycle=self.cycle,
            title="Ship feature X",
            progress=50,
            status=GoalStatus.IN_PROGRESS,
        )
        PerformanceReview.objects.create(
            employee=self.data["employee"],
            cycle=self.cycle,
            reviewer=self.data["manager_user"],
            status=ReviewStatus.SELF_REVIEW,
        )

    def test_employee_sees_own_goals(self):
        self.client.login(username="emp", password="testpass123")
        response = self.client.get(reverse("performance:goals"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ship feature X")

    def test_employee_can_create_goal(self):
        self.client.login(username="emp", password="testpass123")
        response = self.client.get(reverse("performance:goal_create"))
        self.assertEqual(response.status_code, 200)

    def test_reviews_list(self):
        self.client.login(username="emp", password="testpass123")
        response = self.client.get(reverse("performance:reviews"))
        self.assertEqual(response.status_code, 200)

    def test_hr_sees_review_cycles(self):
        self.client.login(username="hr_admin", password="testpass123")
        response = self.client.get(reverse("performance:cycles"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Q1 Review")
