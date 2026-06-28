"""NexusHR — Multi-tenant HR SaaS

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
- **Stripe** — subscriptions, checkout, customer portal, webhooks
- **PostgreSQL + Gunicorn + Docker** — production deployment

## SaaS Features

- **Subdomain multi-tenancy** — each customer gets `yourcompany.localhost` (or `yourcompany.nexushr.com` in production)
- **Self-serve signup** — create workspace, admin account, and trial subscription
- **Subscription plans** — Starter, Pro, Enterprise with module entitlements and employee seat limits
- **Stripe billing** — checkout, customer portal, webhook lifecycle (dev mode works without Stripe keys)
- **Marketing site** — landing page, pricing, terms, privacy policy
- **Tenant isolation** — all HR data scoped by company

## Subscription Plans

| Plan | Employees | Modules |
|------|-----------|---------|
| Starter | 25 | Leave, attendance, employees, org, announcements |
| Pro | 100 | Starter + recruitment, performance, expenses |
| Enterprise | Unlimited | Full suite including payroll |

## User Roles

| Role | Access |
|------|--------|
| Super Admin | Full system access, billing, Django admin |
| HR Admin | All HR modules, employee management, announcements |
| HR Manager | HR operations + approvals |
| Department Manager | Team leave/expense approvals, direct reports |
| Recruiter | Job postings, applicants, recruitment pipeline |
| Employee | Self-service: profile, leave, attendance, payslips, expenses |

## Quick Start (Development)

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_plans
python manage.py seed_demo
python manage.py runserver
```

- **Marketing site:** http://localhost:8000/
- **Demo tenant app:** http://demo.localhost:8000/
- **Sign up new tenant:** http://localhost:8000/signup/

Demo accounts (at `demo.localhost:8000`):

| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | Super Admin |
| hr.admin | hr123 | HR Admin |
| manager | mgr123 | Department Manager |
| employee | emp123 | Employee |
| recruiter | rec123 | Recruiter |

## Stripe Configuration (Optional)

Copy `.env.example` to `.env` and set:

```bash
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

Without Stripe keys, signups activate subscriptions in dev mode automatically.

## Production (Docker)

```bash
docker compose up --build
```

Uses PostgreSQL, Gunicorn, and production Django settings. Set `DJANGO_SECRET_KEY` and Stripe env vars in `docker-compose.yml` or your deployment platform.

## AWS Deployment (SST)

For staging and production on AWS (ECS Fargate, RDS, ALB, auto-scaling), see [docs/sst-deployment.md](docs/sst-deployment.md).

## Development

```bash
pip install -r requirements-dev.txt
pre-commit install
python manage.py test
```

### Quality checks

```bash
pre-commit run --all-files
```

CI runs lint and tests on every push/PR to `main` via GitHub Actions.

## Project Structure

```
tenancy/        — Subdomain middleware, tenant scoping, mixins
billing/        — Plans, subscriptions, Stripe, entitlements
marketing/      — Landing, pricing, signup, legal pages
accounts/       — Custom User model, roles, auth
organization/   — Company (tenant), departments, locations, job titles
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
