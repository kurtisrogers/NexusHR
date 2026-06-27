from datetime import date
from decimal import Decimal

from accounts.models import User, UserRole
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
) -> User:
    return User.objects.create_user(
        username=username,
        password=password,
        role=role,
        first_name=first_name,
        last_name=last_name,
    )


def create_company(name: str = "Acme Corp") -> Company:
    return Company.objects.create(name=name)


def create_department(company: Company, name: str = "Engineering") -> Department:
    return Department.objects.create(company=company, name=name)


def create_employee(
    user: User,
    *,
    employee_id: str,
    hire_date: date | None = None,
    department: Department | None = None,
) -> Employee:
    return Employee.objects.create(
        user=user,
        employee_id=employee_id,
        hire_date=hire_date or date(2024, 1, 15),
        department=department,
    )


def create_leave_type(
    *,
    name: str = "Annual Leave",
    code: str = "AL",
    default_days: int = 20,
) -> LeaveType:
    return LeaveType.objects.create(
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
