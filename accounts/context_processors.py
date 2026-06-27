from .models import UserRole


def user_context(request):
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return {}
    return {
        "user_role": user.role,
        "user_role_label": UserRole(user.role).label,
        "is_hr_staff": user.is_hr_staff,
        "is_manager_or_above": user.is_manager_or_above,
        "can_recruit": user.can_recruit,
    }
