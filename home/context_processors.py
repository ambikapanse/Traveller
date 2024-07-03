from dashboard.models import Profile

def profile_picture(request):
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
            profile_picture_url = profile.profile_picture.url if profile.profile_picture else None
        except Profile.DoesNotExist:
            profile_picture_url = None
        return {'profile_picture_url': profile_picture_url}
    return {}