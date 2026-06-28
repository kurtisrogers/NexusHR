from django.db.models.signals import post_migrate
from django.dispatch import receiver

from billing.entitlements import DEFAULT_PLANS
from billing.models import Plan


@receiver(post_migrate)
def seed_default_plans(sender, **kwargs):
    if sender.name != "billing":
        return
    for plan_data in DEFAULT_PLANS:
        Plan.objects.update_or_create(
            slug=plan_data["slug"],
            defaults=plan_data,
        )
