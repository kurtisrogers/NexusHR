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

### Running tests

```bash
python manage.py test              # all 57 tests across 11 apps
python manage.py test leave        # single app
python manage.py test accounts.tests.UserModelTests  # single class
```

Tests also run automatically in **GitHub Actions** on every push/PR to `main` (`.github/workflows/tests.yml`).

### Pre-commit hooks

Install dev dependencies and enable hooks:

```bash
pip install -r requirements-dev.txt
pre-commit install
pre-commit run --all-files   # run manually on entire repo
```

Hooks run automatically before each commit:

| Hook | Purpose |
|------|---------|
| trailing-whitespace / end-of-file-fixer | File hygiene |
| check-yaml / check-merge-conflict / detect-private-key | Safety checks |
| ruff + ruff-format | Lint and format Python (config in `pyproject.toml`) |
| django-check | `python manage.py check` |
| django-tests | Full test suite |

```bash
python manage.py createsuperuser  # optional additional admin
```

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
