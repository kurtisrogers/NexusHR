def tenant_context(request):
    tenant = getattr(request, "tenant", None)
    ctx = {
        "tenant": tenant,
        "is_public_site": getattr(request, "is_public_site", False),
        "feature_access": {},
        "tenant_plan": None,
        "subscription_active": False,
    }
    if tenant:
        from billing.entitlements import Feature, get_plan, has_feature, subscription_is_active

        plan = get_plan(tenant)
        ctx["tenant_plan"] = plan
        ctx["subscription_active"] = subscription_is_active(tenant)
        ctx["plan_features"] = plan.features if plan else []
        ctx["feature_access"] = {feature: has_feature(tenant, feature) for feature in Feature.ALL}
    return ctx
