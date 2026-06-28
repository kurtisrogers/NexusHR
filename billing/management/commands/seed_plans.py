from django.core.management.base import BaseCommand

from billing.entitlements import DEFAULT_PLANS
from billing.models import Plan


class Command(BaseCommand):
    help = "Seed or update subscription plans"

    def handle(self, *args, **options):
        for plan_data in DEFAULT_PLANS:
            plan, created = Plan.objects.update_or_create(
                slug=plan_data["slug"],
                defaults=plan_data,
            )
            action = "Created" if created else "Updated"
            self.stdout.write(f"{action} plan: {plan.name}")
        self.stdout.write(self.style.SUCCESS("Plans seeded successfully."))
