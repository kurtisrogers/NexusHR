"""NexusHR — Human Resource Management System

Inspired by industry-leading platforms:
- **BambooHR**: Core HR, onboarding, time-off, ATS, performance reviews
- **Workday**: Unified employee records, payroll, talent management, analytics
- **Odoo HR**: Employees, recruitment, appraisals, expenses, fleet
- **SAP SuccessFactors**: Enterprise roles, review cycles, policy management

## Tech Stack

- **Django 5** — backend, ORM, auth, admin
- **HTMX** — dynamic partial updates (leave approvals, clock in/out, recruitment pipeline)
- **Alpine.js** — responsive sidebar, lightweight interactivity
- **Pico CSS** — clean, semantic, classless styling

## User Roles

| Role | Access |
|------|--------|
| Super Admin | Full system access, Django admin |
| HR Admin | All HR modules, employee management, announcements |
| HR Manager | HR operations + approvals |
| Department Manager | Team leave/expense approvals, direct reports |
| Recruiter | Job postings, applicants, recruitment pipeline |
| Employee | Self-service: profile, leave, attendance, payslips, expenses |

## Modules

1. **Dashboard** — KPIs, announcements, headcount analytics
2. **Employees** — profiles, org structure, documents
3. **Organization** — departments, locations, job titles
4. **Leave** — types, balances, requests, approval workflow
5. **Attendance** — clock in/out, timesheets
6. **Recruitment** — job postings, ATS pipeline, stage management
7. **Performance** — goals, review cycles, performance reviews
8. **Payroll** — salary structures, payslips
9. **Expenses** — claims, categories, approval workflow
10. **Announcements & Policies** — company communications

## Quick Start

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Visit http://127.0.0.1:8000/ and sign in with a demo account:

| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | Super Admin |
| hr.admin | hr123 | HR Admin |
| manager | mgr123 | Department Manager |
| employee | emp123 | Employee |
| recruiter | rec123 | Recruiter |

## Development

```bash
pip install -r requirements-dev.txt
pre-commit install
python manage.py test
python manage.py createsuperuser  # optional additional admin
```

### Quality checks

Local hooks run linting, formatting, Django checks, and the test suite before each commit:

```bash
pre-commit run --all-files
```

CI runs the same checks on every push and pull request to `main` via GitHub Actions (`.github/workflows/ci.yml`). To block merges until CI passes, enable branch protection on `main` and require the **Lint** and **Test** status checks.

## Project Structure

```
accounts/       — Custom User model, roles, auth
organization/   — Company, departments, locations, job titles
employees/      — Employee profiles, documents
leave/          — Leave management
attendance/     — Time tracking
recruitment/    — ATS & job postings
performance/    — Goals & reviews
payroll/        — Compensation
expenses/       — Expense claims
announcements/  — Communications & policies
reports/        — Dashboard & analytics
templates/      — HTMX-ready HTML templates
static/         — Custom CSS
```
