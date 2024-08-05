# myapp/context_processors.py
from django.conf import settings
from django.shortcuts import get_object_or_404
from dashboard.models import Profile

def profile_picture(request):
    if request.user.is_authenticated:
        profile = get_object_or_404(Profile, user=request.user)
        profile_picture_url = profile.profile_picture.url if profile.profile_picture else None
    else:
        profile_picture_url = None
    return {'profile_picture_url': profile_picture_url}
