def pending_accounts_count(request):
    """Expose the count of pending account registrations to staff users."""
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return {}
    if not (user.is_superuser or user.is_staff or user.has_perm("cmms.can_approve_accounts")):
        return {}

    from .models import Profile

    count = Profile.objects.filter(approval_status=Profile.APPROVAL_PENDING).count()
    return {"pending_accounts_count": count}
