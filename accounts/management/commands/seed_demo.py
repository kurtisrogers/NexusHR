"""Seed NexusHR with demo data inspired by BambooHR / Workday / Odoo HR modules."""

from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import User, UserRole
from announcements.models import Announcement, PolicyDocument
from attendance.models import AttendanceRecord, AttendanceStatus
from employees.models import Employee, EmploymentStatus, EmploymentType
from expenses.models import ExpenseCategory, ExpenseClaim, ExpenseStatus
from leave.models import LeaveBalance, LeaveRequest, LeaveRequestStatus, LeaveType
from organization.models import Company, Department, JobTitle, Location
from payroll.models import PayFrequency, Payslip, PayslipStatus, SalaryStructure
from performance.models import (
    Goal,
    GoalStatus,
    PerformanceReview,
    ReviewCycle,
    ReviewCycleStatus,
    ReviewStatus,
)
from recruitment.models import Applicant, Application, ApplicationStage, JobPosting, JobStatus


class Command(BaseCommand):
    help = "Populate the database with demo HR data"

    def handle(self, *args, **options):
        if User.objects.filter(username="admin").exists():
            self.stdout.write("Demo data already exists. Skipping.")
            return

        self.stdout.write("Seeding NexusHR demo data…")

        company = Company.objects.create(
            name="Nexus Technologies",
            legal_name="Nexus Technologies Inc.",
            email="hr@nexustech.example",
            website="https://nexustech.example",
            founded_year=2015,
        )

        hq = Location.objects.create(
            company=company,
            name="San Francisco HQ",
            address="100 Market Street",
            city="San Francisco",
            country="USA",
            is_headquarters=True,
        )
        Location.objects.create(
            company=company,
            name="London Office",
            city="London",
            country="UK",
        )

        users = {
            "admin": User.objects.create_superuser(
                "admin",
                "admin@nexustech.example",
                "admin123",
                first_name="System",
                last_name="Admin",
                role=UserRole.SUPER_ADMIN,
            ),
            "hr.admin": self._user(
                "hr.admin",
                "hr@nexustech.example",
                "hr123",
                "Helen",
                "Reyes",
                UserRole.HR_ADMIN,
            ),
            "manager": self._user(
                "manager",
                "manager@nexustech.example",
                "mgr123",
                "Marcus",
                "Chen",
                UserRole.MANAGER,
            ),
            "employee": self._user(
                "employee",
                "employee@nexustech.example",
                "emp123",
                "Emily",
                "Johnson",
                UserRole.EMPLOYEE,
            ),
            "recruiter": self._user(
                "recruiter",
                "rec@nexustech.example",
                "rec123",
                "Rachel",
                "Kim",
                UserRole.RECRUITER,
            ),
        }

        engineering = Department.objects.create(
            company=company,
            name="Engineering",
            code="ENG",
            manager=users["manager"],
        )
        hr_dept = Department.objects.create(
            company=company,
            name="Human Resources",
            code="HR",
            manager=users["hr.admin"],
        )
        Department.objects.create(
            company=company,
            name="Sales",
            code="SLS",
        )

        titles = {
            "swe": JobTitle.objects.create(
                title="Software Engineer",
                department=engineering,
                level=3,
                min_salary=90000,
                max_salary=140000,
            ),
            "mgr": JobTitle.objects.create(
                title="Engineering Manager",
                department=engineering,
                level=5,
                min_salary=130000,
                max_salary=180000,
            ),
            "hr": JobTitle.objects.create(
                title="HR Specialist",
                department=hr_dept,
                level=3,
                min_salary=65000,
                max_salary=95000,
            ),
        }

        today = date.today()
        mgr_emp = Employee.objects.create(
            user=users["manager"],
            employee_id="EMP-001",
            department=engineering,
            job_title=titles["mgr"],
            location=hq,
            employment_type=EmploymentType.FULL_TIME,
            status=EmploymentStatus.ACTIVE,
            hire_date=today - timedelta(days=1200),
        )
        Employee.objects.create(
            user=users["hr.admin"],
            employee_id="EMP-002",
            department=hr_dept,
            job_title=titles["hr"],
            location=hq,
            employment_type=EmploymentType.FULL_TIME,
            status=EmploymentStatus.ACTIVE,
            hire_date=today - timedelta(days=800),
        )
        emp = Employee.objects.create(
            user=users["employee"],
            employee_id="EMP-003",
            department=engineering,
            job_title=titles["swe"],
            location=hq,
            manager=mgr_emp,
            employment_type=EmploymentType.FULL_TIME,
            status=EmploymentStatus.ACTIVE,
            hire_date=today - timedelta(days=400),
        )
        Employee.objects.create(
            user=users["recruiter"],
            employee_id="EMP-004",
            department=hr_dept,
            job_title=titles["hr"],
            location=hq,
            employment_type=EmploymentType.FULL_TIME,
            status=EmploymentStatus.ACTIVE,
            hire_date=today - timedelta(days=300),
        )

        leave_types = [
            LeaveType.objects.create(
                name="Annual Leave", code="AL", default_days=20, color="#3b82f6"
            ),
            LeaveType.objects.create(
                name="Sick Leave", code="SL", default_days=10, color="#ef4444"
            ),
            LeaveType.objects.create(
                name="Personal Leave", code="PL", default_days=5, is_paid=False, color="#8b5cf6"
            ),
        ]
        year = today.year
        for lt in leave_types:
            LeaveBalance.objects.create(
                employee=emp,
                leave_type=lt,
                year=year,
                allocated=lt.default_days,
                used=2 if lt.code == "AL" else 0,
            )

        LeaveRequest.objects.create(
            employee=emp,
            leave_type=leave_types[0],
            start_date=today + timedelta(days=14),
            end_date=today + timedelta(days=16),
            days=3,
            reason="Family vacation",
            status=LeaveRequestStatus.PENDING,
        )

        for i in range(5):
            d = today - timedelta(days=i)
            AttendanceRecord.objects.create(
                employee=emp,
                date=d,
                clock_in=timezone.datetime(2000, 1, 1, 9, 0).time(),
                clock_out=timezone.datetime(2000, 1, 1, 17, 30).time(),
                status=AttendanceStatus.PRESENT,
                hours_worked=Decimal("8.5"),
            )

        job = JobPosting.objects.create(
            title="Senior Backend Developer",
            department=engineering,
            job_title=titles["swe"],
            description="Build scalable HR and workforce platforms with Django.",
            requirements="5+ years Python/Django experience. HTMX knowledge a plus.",
            location="San Francisco / Remote",
            status=JobStatus.OPEN,
            posted_by=users["recruiter"],
            openings=2,
            salary_min=120000,
            salary_max=160000,
            closing_date=today + timedelta(days=60),
        )
        applicant = Applicant.objects.create(
            first_name="Alex",
            last_name="Rivera",
            email="alex.rivera@example.com",
            phone="+1-555-0100",
            source="LinkedIn",
        )
        Application.objects.create(
            job=job,
            applicant=applicant,
            stage=ApplicationStage.INTERVIEW,
            rating=4,
        )

        cycle = ReviewCycle.objects.create(
            name=f"Q2 {year} Performance Review",
            start_date=today - timedelta(days=30),
            end_date=today + timedelta(days=30),
            status=ReviewCycleStatus.ACTIVE,
        )
        Goal.objects.create(
            employee=emp,
            cycle=cycle,
            title="Ship leave management module",
            progress=75,
            status=GoalStatus.IN_PROGRESS,
            target_date=today + timedelta(days=45),
        )
        PerformanceReview.objects.create(
            employee=emp,
            cycle=cycle,
            reviewer=users["manager"],
            status=ReviewStatus.MANAGER_REVIEW,
            self_rating=4,
            self_comments="Strong quarter with major feature deliveries.",
        )

        for _u, emp_obj, base in [
            (users["manager"], mgr_emp, 150000),
            (users["employee"], emp, 115000),
        ]:
            SalaryStructure.objects.create(
                employee=emp_obj,
                base_salary=base,
                housing_allowance=5000,
                transport_allowance=2000,
                pay_frequency=PayFrequency.MONTHLY,
                effective_date=today - timedelta(days=365),
            )
            gross = Decimal(base) + Decimal("7000")
            tax = gross * Decimal("0.22")
            Payslip.objects.create(
                employee=emp_obj,
                period_start=today.replace(day=1),
                period_end=today,
                base_salary=base,
                allowances=7000,
                deductions=500,
                tax=tax,
                net_pay=gross - tax - 500,
                status=PayslipStatus.PAID,
            )

        travel = ExpenseCategory.objects.create(name="Travel", code="TRV", max_amount=5000)
        meals = ExpenseCategory.objects.create(name="Meals", code="MLS", max_amount=200)
        ExpenseClaim.objects.create(
            employee=emp,
            category=travel,
            title="Client site visit — Austin",
            amount=Decimal("342.50"),
            expense_date=today - timedelta(days=5),
            status=ExpenseStatus.SUBMITTED,
        )
        ExpenseClaim.objects.create(
            employee=emp,
            category=meals,
            title="Team lunch",
            amount=Decimal("86.00"),
            expense_date=today - timedelta(days=2),
            status=ExpenseStatus.APPROVED,
            approver=users["manager"],
        )

        Announcement.objects.create(
            title="Welcome to NexusHR!",
            content="Our new HR platform is live. Explore leave, attendance, payroll, and more from your dashboard.",
            author=users["hr.admin"],
            priority="high",
            is_pinned=True,
        )
        Announcement.objects.create(
            title="Q2 Review Cycle Open",
            content="The Q2 performance review cycle is now active. Please complete your self-assessment by month end.",
            author=users["hr.admin"],
            department=engineering,
        )

        PolicyDocument.objects.create(
            title="Remote Work Policy",
            category="Workplace",
            content="Employees may work remotely up to 3 days per week with manager approval.",
            version="2.1",
            effective_date=today - timedelta(days=90),
        )
        PolicyDocument.objects.create(
            title="Code of Conduct",
            category="Compliance",
            content="All employees must adhere to our professional standards and anti-harassment policies.",
            version="1.0",
            effective_date=today - timedelta(days=365),
        )

        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully."))
        self.stdout.write("Login: admin / admin123 (or see login page for all demo accounts)")

    def _user(self, username, email, password, first, last, role):
        return User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first,
            last_name=last,
            role=role,
        )
