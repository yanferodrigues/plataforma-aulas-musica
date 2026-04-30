from .models import Profile


def user_profile(request):
    if not request.user.is_authenticated:
        return {'user_profile': None}
    try:
        return {'user_profile': request.user.profile}
    except Profile.DoesNotExist:
        return {'user_profile': None}
