from .models import UserProfile

def global_profile(request):
    """
    Context processor to ensure user_profile is available globally across all templates
    without throwing RelatedObjectDoesNotExist.
    """
    if request.user.is_authenticated:
        try:
            profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=request.user)
        return {'user_profile': profile}
    return {}
