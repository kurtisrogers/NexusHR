"""Shared helpers for NexusHR tests."""

from datetime import date, timedelta

from accounts.models import User, UserRole
from employees.models import Employee, EmploymentStatus, EmploymentType
from expenses.models import ExpenseCategory, ExpenseClaim, ExpenseStatus
from leave.models import LeaveRequest, LeaveRequestStatus, LeaveType
from organization.models import Company, Department
from recruitment.models import Applicant, Application, ApplicationStage, JobPosting, JobStatus


def create_company(name="Test Co"):
    return Company.objects.create(name=name, email=f"hr@{name.lower().replace(' ', '')}.example")


def create_department(company=None, name="Engineering", manager=None):
    company = company or create_company()
    return Department.objects.create(company=company, name=name, code="ENG", manager=manager)


def create_user(username, role=UserRole.EMPLOYEE, password="testpass123", **kwargs):
    return User.objects.create_user(
        username=username,
        password=password,
        role=role,
        email=f"{username}@example.com",
        first_name=kwargs.pop("first_name", username.title()),
        last_name=kwargs.pop("last_name", "User"),
        **kwargs,
    )


def create_employee(user, employee_id="EMP-100", department=None, manager=None, **kwargs):
    return Employee.objects.create(
        user=user,
        employee_id=employee_id,
        department=department,
        manager=manager,
        hire_date=kwargs.pop("hire_date", date.today() - timedelta(days=365)),
        employment_type=EmploymentType.FULL_TIME,
        status=EmploymentStatus.ACTIVE,
        **kwargs,
    )


def create_hr_setup():
    """Return a dict with company, department, manager, employee, hr_admin users."""
    company = create_company("Nexus Test")
    hr_admin = create_user("hr_admin", UserRole.HR_ADMIN)
    manager_user = create_user("mgr", UserRole.MANAGER)
    employee_user = create_user("emp", UserRole.EMPLOYEE)
    dept = create_department(company=company, name="Engineering", manager=manager_user)
    manager = create_employee(manager_user, "EMP-MGR", department=dept)
    employee = create_employee(
        employee_user,
        "EMP-001",
        department=dept,
        manager=manager,
    )
    create_employee(hr_admin, "EMP-HR", department=dept)
    return {
        "company": company,
        "department": dept,
        "hr_admin": hr_admin,
        "manager_user": manager_user,
        "manager": manager,
        "employee_user": employee_user,
        "employee": employee,
    }


def create_leave_type(name="Annual Leave", code="AL", default_days=20):
    return LeaveType.objects.create(name=name, code=code, default_days=default_days)


def create_leave_request(employee, leave_type=None, status=LeaveRequestStatus.PENDING, **kwargs):
    leave_type = leave_type or create_leave_type()
    start = kwargs.pop("start_date", date.today() + timedelta(days=7))
    end = kwargs.pop("end_date", start + timedelta(days=2))
    return LeaveRequest.objects.create(
        employee=employee,
        leave_type=leave_type,
        start_date=start,
        end_date=end,
        days=3,
        status=status,
        **kwargs,
    )


def create_expense_category(name="Travel", code=None):
    if code is None:
        code = f"TRV{ExpenseCategory.objects.count()}"
    return ExpenseCategory.objects.create(name=name, code=code)


def create_expense_claim(employee, status=ExpenseStatus.SUBMITTED, **kwargs):
    category = kwargs.pop("category", None) or create_expense_category()
    return ExpenseClaim.objects.create(
        employee=employee,
        category=category,
        title=kwargs.pop("title", "Client visit"),
        amount=kwargs.pop("amount", "150.00"),
        expense_date=kwargs.pop("expense_date", date.today()),
        status=status,
        **kwargs,
    )


def create_job_posting(department=None, posted_by=None, status=JobStatus.OPEN):
    department = department or create_department()
    posted_by = posted_by or create_user("poster", UserRole.RECRUITER)
    return JobPosting.objects.create(
        title="Software Engineer",
        department=department,
        description="Build great software.",
        status=status,
        posted_by=posted_by,
    )


def create_application(job=None, stage=ApplicationStage.APPLIED):
    job = job or create_job_posting()
    applicant = Applicant.objects.create(
        first_name="Jane",
        last_name="Doe",
        email="jane@example.com",
    )
    return Application.objects.create(job=job, applicant=applicant, stage=stage)
