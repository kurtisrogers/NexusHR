"""Stripe integration with dev-mode fallback when keys are not configured."""

from __future__ import annotations

import contextlib
import logging
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from billing.models import Plan, Subscription, SubscriptionStatus
from organization.models import Company

logger = logging.getLogger(__name__)


def stripe_enabled() -> bool:
    return bool(settings.STRIPE_SECRET_KEY)


def _get_stripe():
    import stripe

    stripe.api_key = settings.STRIPE_SECRET_KEY
    return stripe


def create_trial_subscription(company: Company, plan: Plan) -> Subscription:
    trial_days = settings.BILLING_TRIAL_DAYS
    return Subscription.objects.create(
        company=company,
        plan=plan,
        status=SubscriptionStatus.TRIALING,
        trial_ends_at=timezone.now() + timedelta(days=trial_days),
    )


def create_checkout_session(company: Company, plan: Plan, success_url: str, cancel_url: str) -> str:
    if not stripe_enabled() or not plan.stripe_price_id:
        subscription, _created = Subscription.objects.get_or_create(
            company=company,
            defaults={
                "plan": plan,
                "status": SubscriptionStatus.ACTIVE,
            },
        )
        if not _created:
            subscription.plan = plan
            subscription.status = SubscriptionStatus.ACTIVE
            subscription.save(update_fields=["plan", "status", "updated_at"])
        return success_url

    stripe = _get_stripe()
    subscription = getattr(company, "subscription", None)
    customer_id = subscription.stripe_customer_id if subscription else ""

    if not customer_id:
        customer = stripe.Customer.create(
            email=company.email or f"admin@{company.subdomain}.local",
            name=company.name,
            metadata={"company_id": str(company.id), "subdomain": company.subdomain},
        )
        customer_id = customer.id
        if subscription:
            subscription.stripe_customer_id = customer_id
            subscription.save(update_fields=["stripe_customer_id", "updated_at"])

    session = stripe.checkout.Session.create(
        mode="subscription",
        customer=customer_id,
        line_items=[{"price": plan.stripe_price_id, "quantity": 1}],
        success_url=success_url,
        cancel_url=cancel_url,
        subscription_data={
            "trial_period_days": settings.BILLING_TRIAL_DAYS,
            "metadata": {"company_id": str(company.id)},
        },
        metadata={"company_id": str(company.id), "plan_slug": plan.slug},
    )
    return session.url


def create_customer_portal_session(company: Company, return_url: str) -> str:
    if not stripe_enabled():
        return return_url

    subscription = company.subscription
    if not subscription.stripe_customer_id:
        return return_url

    stripe = _get_stripe()
    session = stripe.billing_portal.Session.create(
        customer=subscription.stripe_customer_id,
        return_url=return_url,
    )
    return session.url


def handle_webhook(payload: bytes, sig_header: str) -> None:
    if not stripe_enabled():
        return

    stripe = _get_stripe()
    event = stripe.Webhook.construct_event(
        payload,
        sig_header,
        settings.STRIPE_WEBHOOK_SECRET,
    )

    handlers = {
        "checkout.session.completed": _handle_checkout_completed,
        "customer.subscription.updated": _handle_subscription_updated,
        "customer.subscription.deleted": _handle_subscription_deleted,
        "invoice.payment_failed": _handle_payment_failed,
    }
    handler = handlers.get(event["type"])
    if handler:
        handler(event["data"]["object"])


def _sync_subscription_from_stripe(stripe_sub: dict) -> None:
    company_id = stripe_sub.get("metadata", {}).get("company_id")
    if not company_id:
        return

    try:
        company = Company.objects.get(pk=company_id)
    except Company.DoesNotExist:
        logger.warning("Stripe subscription for unknown company %s", company_id)
        return

    subscription, _created = Subscription.objects.get_or_create(
        company=company,
        defaults={"plan": Plan.objects.filter(is_active=True).order_by("sort_order").first()},
    )
    subscription.stripe_subscription_id = stripe_sub.get("id", "")
    subscription.stripe_customer_id = stripe_sub.get("customer", "")
    subscription.status = stripe_sub.get("status", SubscriptionStatus.ACTIVE)
    subscription.cancel_at_period_end = stripe_sub.get("cancel_at_period_end", False)

    period_end = stripe_sub.get("current_period_end")
    if period_end:
        subscription.current_period_end = timezone.datetime.fromtimestamp(
            period_end,
            tz=timezone.get_current_timezone(),
        )

    trial_end = stripe_sub.get("trial_end")
    if trial_end:
        subscription.trial_ends_at = timezone.datetime.fromtimestamp(
            trial_end,
            tz=timezone.get_current_timezone(),
        )

    plan_slug = stripe_sub.get("metadata", {}).get("plan_slug")
    if plan_slug:
        with contextlib.suppress(Plan.DoesNotExist):
            subscription.plan = Plan.objects.get(slug=plan_slug)

    subscription.save()


def _handle_checkout_completed(session: dict) -> None:
    company_id = session.get("metadata", {}).get("company_id")
    plan_slug = session.get("metadata", {}).get("plan_slug")
    if not company_id:
        return

    try:
        company = Company.objects.get(pk=company_id)
    except Company.DoesNotExist:
        return

    plan = Plan.objects.filter(slug=plan_slug).first() if plan_slug else None
    subscription, _created = Subscription.objects.get_or_create(
        company=company,
        defaults={"plan": plan or Plan.objects.filter(is_active=True).first()},
    )
    subscription.stripe_customer_id = session.get("customer", "")
    subscription.stripe_subscription_id = session.get("subscription", "")
    if plan:
        subscription.plan = plan
    subscription.status = SubscriptionStatus.ACTIVE
    subscription.save()


def _handle_subscription_updated(stripe_sub: dict) -> None:
    _sync_subscription_from_stripe(stripe_sub)


def _handle_subscription_deleted(stripe_sub: dict) -> None:
    _sync_subscription_from_stripe(stripe_sub)
    sub_id = stripe_sub.get("id")
    Subscription.objects.filter(stripe_subscription_id=sub_id).update(
        status=SubscriptionStatus.CANCELED,
    )


def _handle_payment_failed(invoice: dict) -> None:
    customer_id = invoice.get("customer")
    if not customer_id:
        return
    Subscription.objects.filter(stripe_customer_id=customer_id).update(
        status=SubscriptionStatus.PAST_DUE,
    )
