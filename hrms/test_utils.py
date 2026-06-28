from datetime import date
from decimal import Decimal

from accounts.models import User, UserRole
from billing.models import Plan, Subscription, SubscriptionStatus
from employees.models import Employee
from leave.models import LeaveBalance, LeaveType
from organization.models import Company, Department


def create_user(
    username: str,
    *,
    password: str = "testpass123",
    role: str = UserRole.EMPLOYEE,
    first_name: str = "Test",
    last_name: str = "User",
    company: Company | None = None,
) -> User:
    return User.objects.create_user(
        username=username,
        password=password,
        role=role,
        first_name=first_name,
        last_name=last_name,
        company=company,
    )


def create_company(name: str = "Acme Corp", subdomain: str | None = None) -> Company:
    if subdomain is None:
        subdomain = name.lower().replace(" ", "-")[:20]
    return Company.objects.create(name=name, subdomain=subdomain)


def create_department(company: Company, name: str = "Engineering") -> Department:
    return Department.objects.create(company=company, name=name)


def create_employee(
    user: User,
    *,
    employee_id: str,
    hire_date: date | None = None,
    department: Department | None = None,
    company: Company | None = None,
) -> Employee:
    resolved_company = company or user.company
    if resolved_company is None:
        raise ValueError("company is required for employees")
    return Employee.objects.create(
        user=user,
        company=resolved_company,
        employee_id=employee_id,
        hire_date=hire_date or date(2024, 1, 15),
        department=department,
    )


def create_leave_type(
    *,
    company: Company,
    name: str = "Annual Leave",
    code: str = "AL",
    default_days: int = 20,
) -> LeaveType:
    return LeaveType.objects.create(
        company=company,
        name=name,
        code=code,
        default_days=default_days,
    )


def create_leave_balance(
    employee: Employee,
    leave_type: LeaveType,
    *,
    year: int = 2024,
    allocated: Decimal = Decimal("20"),
    used: Decimal = Decimal("0"),
    carried_over: Decimal = Decimal("0"),
) -> LeaveBalance:
    return LeaveBalance.objects.create(
        employee=employee,
        leave_type=leave_type,
        year=year,
        allocated=allocated,
        used=used,
        carried_over=carried_over,
    )


def create_tenant_subscription(company: Company, plan_slug: str = "pro") -> Subscription:
    plan = Plan.objects.filter(slug=plan_slug).first()
    if not plan:
        from django.core.management import call_command

        call_command("seed_plans")
        plan = Plan.objects.get(slug=plan_slug)
    return Subscription.objects.create(
        company=company,
        plan=plan,
        status=SubscriptionStatus.ACTIVE,
    )
