from django import template
from django.conf import settings

register = template.Library()

@register.filter
def get_institution_image(college_name):
    """
    Maps college name to its corresponding static image filename.
    Returns the path to the image in the static directory.
    """
    if not college_name:
        return 'images/default_college.jpg'
        
    college_name_lower = college_name.lower()
    
    # Mapping logic
    if 'anna' in college_name_lower and 'university' in college_name_lower:
        return 'images/annauni.jpg'
    elif 'srm' in college_name_lower:
        return 'images/srm.jpg'
    elif 'sla' in college_name_lower:
        return 'images/sla.webp'
    elif 'sathyabama' in college_name_lower or 'sathiyabama' in college_name_lower:
        return 'images/sathiyabama.jpg'
    elif 'niit' in college_name_lower:
        return 'images/niit.jpg'
    elif 'qspiders' in college_name_lower or 'quespyder' in college_name_lower:
        return 'images/quespyder.jpg'
    elif 'green' in college_name_lower:
        return 'images/green.png'
    elif 'besan' in college_name_lower:
        return 'images/besan.png'
    elif 'aptech' in college_name_lower:
        return 'images/aptech.jpeg'
    elif 'two2' in college_name_lower: # Example based on file list
        return 'images/two2.jpg'
    
    # Default fallback
    return None

@register.filter
def get_profile_pic(user):
    """
    Returns the user's profile picture URL if it exists, else None.
    """
    if not user:
        return None
        
    try:
        if hasattr(user, 'userprofile') and user.userprofile.profile_picture:
            return user.userprofile.profile_picture.url
    except Exception:
        pass
        
    return None

