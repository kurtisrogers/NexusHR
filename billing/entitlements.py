"""Plan features and entitlement checks."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from organization.models import Company


class Feature:
    LEAVE = "leave"
    ATTENDANCE = "attendance"
    EMPLOYEES = "employees"
    ORGANIZATION = "organization"
    ANNOUNCEMENTS = "announcements"
    RECRUITMENT = "recruitment"
    PERFORMANCE = "performance"
    EXPENSES = "expenses"
    PAYROLL = "payroll"

    ALL = (
        LEAVE,
        ATTENDANCE,
        EMPLOYEES,
        ORGANIZATION,
        ANNOUNCEMENTS,
        RECRUITMENT,
        PERFORMANCE,
        EXPENSES,
        PAYROLL,
    )

    LABELS = {
        LEAVE: "Leave Management",
        ATTENDANCE: "Time & Attendance",
        EMPLOYEES: "Employee Records",
        ORGANIZATION: "Org Structure",
        ANNOUNCEMENTS: "Announcements & Policies",
        RECRUITMENT: "Recruitment (ATS)",
        PERFORMANCE: "Performance Reviews",
        EXPENSES: "Expense Management",
        PAYROLL: "Payroll",
    }


DEFAULT_PLANS = [
    {
        "slug": "starter",
        "name": "Starter",
        "description": "Core HR for small teams",
        "price_monthly_cents": 2900,
        "max_employees": 25,
        "features": [
            Feature.LEAVE,
            Feature.ATTENDANCE,
            Feature.EMPLOYEES,
            Feature.ORGANIZATION,
            Feature.ANNOUNCEMENTS,
        ],
        "sort_order": 1,
        "is_popular": False,
    },
    {
        "slug": "pro",
        "name": "Pro",
        "description": "Growing teams with talent & performance tools",
        "price_monthly_cents": 7900,
        "max_employees": 100,
        "features": [
            Feature.LEAVE,
            Feature.ATTENDANCE,
            Feature.EMPLOYEES,
            Feature.ORGANIZATION,
            Feature.ANNOUNCEMENTS,
            Feature.RECRUITMENT,
            Feature.PERFORMANCE,
            Feature.EXPENSES,
        ],
        "sort_order": 2,
        "is_popular": True,
    },
    {
        "slug": "enterprise",
        "name": "Enterprise",
        "description": "Full HR suite for larger organizations",
        "price_monthly_cents": 19900,
        "max_employees": 0,
        "features": list(Feature.ALL),
        "sort_order": 3,
        "is_popular": False,
    },
]


def get_subscription(company: Company):
    if hasattr(company, "subscription"):
        return company.subscription
    return None


def get_plan(company: Company):
    subscription = get_subscription(company)
    if subscription and subscription.plan:
        return subscription.plan
    return None


def subscription_is_active(company: Company) -> bool:
    subscription = get_subscription(company)
    if not subscription:
        return False
    return subscription.is_active


def has_feature(company: Company, feature: str) -> bool:
    if not subscription_is_active(company):
        return False
    plan = get_plan(company)
    if not plan:
        return False
    return feature in plan.features


def active_employee_count(company: Company) -> int:
    from employees.models import Employee, EmploymentStatus

    return Employee.objects.filter(company=company, status=EmploymentStatus.ACTIVE).count()


def can_add_employee(company: Company) -> bool:
    plan = get_plan(company)
    if not plan or not subscription_is_active(company):
        return False
    if plan.max_employees == 0:
        return True
    return active_employee_count(company) < plan.max_employees


def employee_limit(company: Company) -> int | None:
    plan = get_plan(company)
    if not plan:
        return None
    if plan.max_employees == 0:
        return None
    return plan.max_employees
