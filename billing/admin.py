from django.contrib import admin

from billing.models import Plan, Subscription


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "price_monthly_cents",
        "max_employees",
        "is_active",
        "sort_order",
    )
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("company", "plan", "status", "stripe_customer_id", "current_period_end")
    list_filter = ("status", "plan")
    search_fields = ("company__name", "company__subdomain", "stripe_customer_id")
