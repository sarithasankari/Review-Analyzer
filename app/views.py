from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Avg
from .models import CollegeReview  # REMOVED: , Institution
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm
from django.views.decorators.csrf import csrf_exempt
import json
import json
from .forms import CollegeReviewForm

class CollegeReviewForm(forms.ModelForm):
    # REMOVED: institution field since Institution model doesn't exist
    college_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter college/institute name'})
    )
    
    class Meta:
        model = CollegeReview
        fields = ['college_name', 'user_name', 'mobile_number', 'education_system', 'staff_review', 
                 'practical_experience', 'fees_structure', 'management_review',
                 'sports_cultural', 'placement_review', 'placement_rating',
                 'travel_expense', 'entrepreneurship_support', 'canteen_available',
                 'canteen_review', 'hostel_available', 'hostel_review',
                 'infrastructure_review', 'security_review', 'overall_rating', 'overall_review']

def index(request):
    """Main index view that renders the index.html template"""
    from django.db.models import Avg, Count
    
    # Define the 9 default institutions to display on the homepage
    default_colleges = [
        {"name": "Anna University", "location": "Guindy, Chennai", "description": "Premier technical university offering engineering, technology and architecture programs with excellent placement opportunities.", "category": "College"},
        {"name": "SLA Institute", "location": "K K Nagar, Chennai", "description": "Leading training institute offering professional courses in software development, data science and digital marketing with placement assistance.", "category": "Institute"},
        {"name": "Sathyabama University", "location": "Jeppiaar Nagar, Chennai", "description": "Private deemed university offering engineering, dental and science programs with strong focus on research and innovation.", "category": "College"},
        {"name": "Green Technology Institute", "location": "Adyar, Chennai", "description": "Specialized institute focusing on sustainable technologies, renewable energy, and environmental conservation programs with hands-on training.", "category": "Institute"},
        {"name": "BesanTech Institute", "location": "T Nagar, Chennai", "description": "Advanced technology institute offering courses in AI, machine learning, data science and software development with industry projects.", "category": "Institute"},
        {"name": "Quespyder Institute", "location": "Velachery, Chennai", "description": "Innovative training institute specializing in coding bootcamps, web development, and software engineering with project-based learning approach.", "category": "Institute"},
        {"name": "SRM University", "location": "Kattankulathur, Chennai", "description": "Deemed university known for engineering, medical and management programs with state-of-the-art infrastructure and international collaborations.", "category": "College"},
        {"name": "NIIT Chennai", "location": "Anna Nagar, Chennai", "description": "Leading IT training institute offering certification courses in programming, data science, cloud computing and digital marketing.", "category": "Institute"},
        {"name": "Aptech Computer Education", "location": "Adyar, Chennai", "description": "Professional computer education institute offering courses in software development, networking, and hardware with placement support.", "category": "Institute"}
    ]
    
    # Query database to aggregate ratings and review count per college name
    db_colleges = CollegeReview.objects.values('college_name').annotate(
        avg_rating=Avg('overall_rating'),
        review_count=Count('id')
    )
    
    # Create a lookup mapping from college_name to aggregated stats
    db_stats = {item['college_name'].lower().strip(): item for item in db_colleges}
    
    # Build list of final colleges to display on homepage
    colleges_list = []
    processed_names = set()
    
    # First, process the default featured colleges
    for dc in default_colleges:
        name_lower = dc['name'].lower().strip()
        stats = db_stats.get(name_lower)
        if stats:
            dc['avg_rating'] = round(stats['avg_rating'], 1)
            dc['review_count'] = stats['review_count']
        else:
            dc['avg_rating'] = 4.5  # default
            dc['review_count'] = 0
        colleges_list.append(dc)
        processed_names.add(name_lower)
        
    # The user requested to only show the original default colleges on the homepage, 
    # so we do not append any extra dynamically submitted colleges here.
            
    # Get all college names for the dropdown search suggestion / general reference
    college_names = sorted(list(set(CollegeReview.objects.values_list('college_name', flat=True).distinct())))
    
    return render(request, 'app/index.html', {
        'colleges': colleges_list,
        'college_names': college_names
    })

def register_view(request):
    if request.method == 'POST':
        # Get form data
        first_name = request.POST.get('firstName')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirmPassword')
        
        # Validate passwords match
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('register')
        
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('register')
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('register')
        
        # Create user
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name
            )
            user.save()
            messages.success(request, "Registration successful! Please login.")
            return redirect('login')
        except Exception as e:
            messages.error(request, f"Error creating account: {str(e)}")
            return redirect('register')
    
    return render(request, 'app/register.html')

def login_view(request):
    # If user is already authenticated, redirect to index
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name}!')
            return redirect('index')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'app/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('index')

@login_required
def review_page(request, college_name=None):
    if request.method == 'POST':
        # Process the review form data
        try:
            # Get form data
            submitted_college_name = request.POST.get('collegeName')
            overall_rating = request.POST.get('overallRating')
            overall_review = request.POST.get('overallReview')
            name = request.POST.get('name')
            mobile = request.POST.get('mobile')
            education = request.POST.get('education', '')
            staff = request.POST.get('staff', '')
            practical = request.POST.get('practical', '')
            fees = request.POST.get('fees', '')
            management = request.POST.get('management', '')
            placement = request.POST.get('placement', '')
            infrastructure = request.POST.get('infrastructure', '')
            
            # Create review object
            review = CollegeReview(
                user=request.user,
                college_name=submitted_college_name,
                user_name=name,
                mobile_number=mobile,
                overall_rating=overall_rating,
                overall_review=overall_review,
                education_system=education,
                staff_review=staff,
                practical_experience=practical,
                fees_structure=fees,
                management_review=management,
                placement_review=placement,
                infrastructure_review=infrastructure,
            )
            review.save()
            
            messages.success(request, 'Thank you for your review! Your feedback has been submitted successfully.')
            return redirect('view_reviews', college_name=submitted_college_name)
            
        except Exception as e:
            messages.error(request, f'Error submitting review: {str(e)}')
    
    return render(request, 'app/review.html', {'college_name': college_name})

def view_reviews(request, college_name):
    try:
        if college_name == "All" or college_name == "all":
            reviews = CollegeReview.objects.all().order_by('-created_at')
            display_name = "All Reviews"
        else:
            # Strip whitespace to handle URL encoding issues or trailing spaces
            college_name_clean = college_name.strip()
            # Use iexact for case-insensitive matching
            reviews = CollegeReview.objects.filter(college_name__iexact=college_name_clean).order_by('-created_at')
            display_name = college_name_clean

        avg_rating = reviews.aggregate(Avg('overall_rating'))['overall_rating__avg'] or 0
        
        # Map for college logos
        logo_map = {
            'Anna University': 'images/annauni.jpg',
            'SLA Institute': 'images/sla.webp',
            'Sathyabama University': 'images/sathiyabama.jpg',
            'Green Technology Institute': 'images/green.png',
            'BesanTech Institute': 'images/besan.png',
            'Quespyder Institute': 'images/quespyder.jpg',
            'Aptech Computer Education': 'images/aptech.jpeg',
        }
        
        context = {
            'college_name': display_name,
            'college_logo': logo_map.get(display_name),
            'reviews': reviews,
            'avg_rating': round(avg_rating, 1),
            'total_reviews': reviews.count(),
            'current_filter': display_name, # Pass cleaned name for active state
        }
        return render(request, 'app/view_reviews.html', context)
    except Exception as e:
        return render(request, 'app/view_reviews.html', {
            'college_name': college_name,
            'reviews': [],
            'avg_rating': 0,
            'total_reviews': 0,
            'current_filter': college_name,
        })

@login_required
def review_form(request):
    if request.method == 'POST':
        form = CollegeReviewForm(request.POST)
        if form.is_valid():
            try:
                review = form.save(commit=False)
                review.user = request.user
                review.save()
                
                messages.success(request, 'Review submitted successfully!')
                return redirect('review_success')
            except Exception as e:
                messages.error(request, f'Error submitting review: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        # Pre-populate user name for logged-in user
        initial_data = {'user_name': f"{request.user.first_name} {request.user.last_name}".strip()}
        if not initial_data['user_name']:
            initial_data['user_name'] = request.user.username
        form = CollegeReviewForm(initial=initial_data)
    
    return render(request, 'app/reviews/review_form.html', {'form': form})

@csrf_exempt
def api_submit_review(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Use authenticated user if available
            if request.user.is_authenticated:
                user = request.user
            else:
                # If not logged in, we can't submit as 'user' is required by model
                return JsonResponse({'success': False, 'error': 'You must be logged in to submit a review.'})

            # Handle integer conversion safely
            def get_int(val):
                if not val: return 0
                try: return int(val)
                except: return 0
                
            def get_bool(val):
                return bool(val) and val != '0' and val != 0

            # Create review with ALL fields
            review = CollegeReview(
                user=user,
                college_name=data.get('college_name', ''),
                user_name=data.get('user_name', request.user.first_name or request.user.username),
                mobile_number=data.get('mobile_number', ''),
                overall_rating=get_int(data.get('overall_rating')),
                overall_review=data.get('overall_review', ''),
                
                # Add missing fields
                education_system=data.get('education_system', ''),
                staff_review=data.get('staff_review', ''),
                practical_experience=data.get('practical_experience', ''),
                fees_structure=data.get('fees_structure', ''),
                management_review=data.get('management_review', ''),
                sports_cultural=data.get('sports_cultural', ''),
                placement_review=data.get('placement_review', ''),
                placement_rating=get_int(data.get('placement_rating')) if data.get('placement_rating') else None,
                travel_expense=data.get('travel_expense', ''),
                entrepreneurship_support=data.get('entrepreneurship_support', ''),
                canteen_available=get_bool(data.get('canteen_available')),
                canteen_review=data.get('canteen_review', ''),
                hostel_available=get_bool(data.get('hostel_available')),
                hostel_review=data.get('hostel_review', ''),
                infrastructure_review=data.get('infrastructure_review', ''),
                security_review=data.get('security_review', ''),
            )
            review.save()
            
            from django.urls import reverse
            redirect_url = reverse('view_reviews', args=[review.college_name])
            
            return JsonResponse({
                'success': True, 
                'message': 'Review submitted successfully!',
                'redirect_url': redirect_url
            })
            
        except Exception as e:
            print(f"Error submitting review: {str(e)}")
            return JsonResponse({'success': False, 'error': f"Server Error: {str(e)}"})


# ... your existing imports and code ...

def review_success(request):
    return render(request, 'reviews/review_success.html')

def review_list(request):
    return redirect('view_reviews', college_name='All')

def review_detail(request, review_id):
    try:
        review = CollegeReview.objects.get(id=review_id)
        return render(request, 'app/reviews/review_detail.html', {'review': review})
    except CollegeReview.DoesNotExist:
        messages.error(request, 'Review not found.')
        return redirect('review_list')

@login_required
def get_user_reviews(request):
    """Display reviews submitted by the current user"""
    # Get all reviews by user
    # RESTRICTION REMOVED: Allow seeing all reviews (filtered by dropdown)
    user_reviews = CollegeReview.objects.filter(user=request.user).order_by('college_name', '-created_at')
    
    # Get distinct colleges for filter dropdown
    # We use a set comprehension to get unique names efficiently in Python 
    # since SQLite/MySQL distinct on text fields can sometimes be tricky with order_by
    colleges = sorted(list(set(review.college_name for review in user_reviews)))
    
    # Filter by college if selected
    selected_college = request.GET.get('college')
    if selected_college and selected_college != 'All':
        reviews = user_reviews.filter(college_name=selected_college).order_by('college_name', '-created_at')
    else:
        reviews = user_reviews
        selected_college = 'All'
        
    context = {
        'reviews': reviews,
        'colleges': colleges,
        'current_filter': selected_college
    }
    return render(request, 'app/reviews/my_reviews.html', context)

@login_required
def profile_view(request):
    """Display and update user profile"""
    from .forms import UserUpdateForm, UserProfileForm
    from .models import UserProfile
    
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user)

    reviews_count = CollegeReview.objects.filter(user=request.user).count()
    likes_received = sum(
        review.likes.count() for review in CollegeReview.objects.filter(user=request.user)
    )
    saved_count = CollegeReview.objects.filter(saves=request.user).count()
    recent_reviews = CollegeReview.objects.filter(user=request.user).order_by('-created_at')[:3]

    user_form = UserUpdateForm(instance=request.user)
    profile_form = UserProfileForm(instance=user_profile)

    if request.method == 'POST':
        # ── AJAX photo-only upload ──────────────────────────────────────
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            if 'profile_picture' not in request.FILES:
                return JsonResponse({'success': False, 'errors': 'No file received.'})

            photo = request.FILES['profile_picture']

            # Validate size (5 MB)
            if photo.size > 5 * 1024 * 1024:
                return JsonResponse({'success': False, 'errors': 'File too large. Maximum size is 5 MB.'})

            # Validate content type (some browsers send image/jpg)
            allowed = ['image/jpeg', 'image/jpg', 'image/png']
            if photo.content_type not in allowed:
                return JsonResponse({'success': False, 'errors': 'Unsupported format. Please upload JPG or PNG.'})

            # Save only the photo field – do NOT touch bio/phone/location
            try:
                user_profile.profile_picture = photo
                user_profile.save(update_fields=['profile_picture'])
                return JsonResponse({'success': True, 'photo_url': user_profile.profile_picture.url})
            except Exception as e:
                return JsonResponse({'success': False, 'errors': f'Server error: {str(e)}'})

        # Regular form submission
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
        else:
            messages.error(request, 'Please fix the errors below.')

    return render(request, 'app/profile.html', {
        'reviews_count': reviews_count,
        'likes_received': likes_received,
        'saved_count': saved_count,
        'recent_reviews': recent_reviews,
        'user': request.user,
        'user_profile': user_profile,
        'user_form': user_form,
        'profile_form': profile_form,
    })


from .forms import CollegeReviewForm, UserUpdateForm, UserProfileForm
from .models import UserProfile
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

@login_required
def settings_view(request):
    # Get or create UserProfile
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user)

    user_form = UserUpdateForm(instance=request.user)
    password_form = PasswordChangeForm(request.user)
    profile_form = UserProfileForm(instance=user_profile)
    
    if request.method == 'POST':
        # DEBUG: Print everything to console
        print("--- SETTINGS VIEW POST ---")
        print("POST Data:", request.POST)
        print("FILES Data:", request.FILES)
        
        if 'update_profile' in request.POST:
            user_form = UserUpdateForm(request.POST, instance=request.user)
            profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
            
            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                print("SUCCESS: Profile updated.")
                messages.success(request, 'Your profile has been updated successfully!')
                return redirect('settings')
            else:
                print("ERROR: Forms invalid.")
                print("User Errors:", user_form.errors)
                print("Profile Errors:", profile_form.errors)
                messages.error(request, 'Please correct the errors in your profile information.')
                
        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                # update_session_auth_hash prevents the user from being logged out
                update_session_auth_hash(request, user)
                messages.success(request, 'Your password was successfully updated! You can now use your new password.')
                return redirect('settings')
            else:
                error_messages = []
                for field in password_form:
                    for error in field.errors:
                        error_messages.append(f"{field.label}: {error}")
                for error in password_form.non_field_errors():
                    error_messages.append(error)
                
                error_str = " | ".join(error_messages)
                messages.error(request, f'Please correct the errors: {error_str}')
        
        elif 'request_verification' in request.POST:
            # Simple simulation for now
            # In a real app, this would send an email or create an admin task
            user_profile.is_verified = True
            user_profile.save()
            messages.success(request, 'Verification request submitted! Your account is now verified (Simulation).')
            return redirect('settings')
                
    return render(request, 'app/settings.html', {
        'user_form': user_form,
        'password_form': password_form,
        'profile_form': profile_form,
        'user_profile': user_profile
    })

# Fallback view in case of import issues
# Fallback view in case of import issues
def simple_review_form(request):
    return render(request, 'reviews/simple_form.html')

def toggle_like(request, review_id):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'not_logged_in'})
    
    if request.method == 'POST':
        try:
            review = get_object_or_404(CollegeReview, id=review_id)
            if request.user in review.likes.all():
                review.likes.remove(request.user)
                liked = False
            else:
                review.likes.add(request.user)
                liked = True
            return JsonResponse({'success': True, 'liked': liked, 'like_count': review.likes.count()})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def toggle_save(request, review_id):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'not_logged_in'})
        
    if request.method == 'POST':
        try:
            review = get_object_or_404(CollegeReview, id=review_id)
            if request.user in review.saves.all():
                review.saves.remove(request.user)
                saved = False
            else:
                review.saves.add(request.user)
                saved = True
            return JsonResponse({'success': True, 'saved': saved})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def add_comment(request, review_id):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'not_logged_in'})
        
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            text = data.get('text', '').strip()
            
            if not text:
                return JsonResponse({'success': False, 'error': 'Comment text cannot be empty'})
                
            review = get_object_or_404(CollegeReview, id=review_id)
            from .models import ReviewComment
            comment = ReviewComment.objects.create(
                review=review,
                user=request.user,
                text=text
            )
            
            return JsonResponse({
                'success': True, 
                'comment_id': comment.id,
                'author': request.user.get_full_name() or request.user.username,
                'text': comment.text,
                'created_at': comment.created_at.strftime("%b %d, %Y, %I:%M %p")
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def toggle_comment_like(request, comment_id):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'not_logged_in'})
    
    if request.method == 'POST':
        try:
            from .models import ReviewComment
            comment = get_object_or_404(ReviewComment, id=comment_id)
            if request.user in comment.likes.all():
                comment.likes.remove(request.user)
                liked = False
            else:
                comment.likes.add(request.user)
                liked = True
            return JsonResponse({'success': True, 'liked': liked, 'like_count': comment.likes.count()})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def dashboard_view(request):
    """View to display detailed review analytics and charts"""
    from django.db.models import Avg, Count
    from django.contrib.auth.models import User
    from app.models import CollegeReview
    
    total_reviews = CollegeReview.objects.count()
    total_colleges = CollegeReview.objects.values('college_name').distinct().count()
    
    avg_platform_rating = CollegeReview.objects.aggregate(Avg('overall_rating'))['overall_rating__avg'] or 0.0
    avg_platform_rating = round(avg_platform_rating, 2)
    
    college_averages = CollegeReview.objects.values('college_name').annotate(
        avg_r=Avg('overall_rating'),
        count_r=Count('id')
    ).order_by('-avg_r', '-count_r')
    
    top_colleges = []
    for item in college_averages[:5]:
        top_colleges.append({
            'name': item['college_name'],
            'avg_rating': round(item['avg_r'], 1),
            'count': item['count_r']
        })
        
    most_reviewed = []
    college_counts = CollegeReview.objects.values('college_name').annotate(
        count_r=Count('id'),
        avg_r=Avg('overall_rating')
    ).order_by('-count_r')[:5]
    
    for item in college_counts:
        most_reviewed.append({
            'name': item['college_name'],
            'count': item['count_r'],
            'avg_rating': round(item['avg_r'], 1)
        })
        
    positive_count = CollegeReview.objects.filter(overall_rating__gte=4).count()
    neutral_count = CollegeReview.objects.filter(overall_rating=3).count()
    negative_count = CollegeReview.objects.filter(overall_rating__lte=2).count()
    
    active_users_raw = CollegeReview.objects.values('user__username', 'user__first_name').annotate(
        count_u=Count('id')
    ).order_by('-count_u')[:5]
    
    active_users = []
    for user_info in active_users_raw:
        if user_info['user__username']:
            display_name = user_info['user__first_name'] or user_info['user__username']
            active_users.append({
                'name': display_name,
                'count': user_info['count_u']
            })
            
    context = {
        'total_reviews': total_reviews,
        'total_colleges': total_colleges,
        'avg_platform_rating': avg_platform_rating,
        'top_colleges': top_colleges,
        'most_reviewed': most_reviewed,
        'sentiment_stats': {
            'positive': positive_count,
            'neutral': neutral_count,
            'negative': negative_count
        },
        'active_users': active_users
    }
    
    return render(request, 'app/dashboard.html', context)


def compare_view(request):
    """View to select and compare two colleges side-by-side"""
    from django.db.models import Avg, Count
    from app.models import CollegeReview
    
    college_names = sorted(list(set(CollegeReview.objects.values_list('college_name', flat=True).distinct())))
    
    college1_name = request.GET.get('college1')
    college2_name = request.GET.get('college2')
    
    comparison_data = None
    
    if college1_name and college2_name:
        reviews1 = CollegeReview.objects.filter(college_name__iexact=college1_name.strip())
        stats1 = reviews1.aggregate(
            avg_overall=Avg('overall_rating'),
            avg_placement=Avg('placement_rating'),
            review_count=Count('id')
        )
        
        total_count1 = stats1['review_count'] or 1
        canteen_yes1 = reviews1.filter(canteen_available=True).count()
        hostel_yes1 = reviews1.filter(hostel_available=True).count()
        
        edu_comments1 = [r.education_system for r in reviews1 if r.education_system][:3]
        staff_comments1 = [r.staff_review for r in reviews1 if r.staff_review][:3]
        infra_comments1 = [r.infrastructure_review for r in reviews1 if r.infrastructure_review][:3]
        placement_comments1 = [r.placement_review for r in reviews1 if r.placement_review][:3]
        fees_comments1 = [r.fees_structure for r in reviews1 if r.fees_structure][:3]
        
        reviews2 = CollegeReview.objects.filter(college_name__iexact=college2_name.strip())
        stats2 = reviews2.aggregate(
            avg_overall=Avg('overall_rating'),
            avg_placement=Avg('placement_rating'),
            review_count=Count('id')
        )
        
        total_count2 = stats2['review_count'] or 1
        canteen_yes2 = reviews2.filter(canteen_available=True).count()
        hostel_yes2 = reviews2.filter(hostel_available=True).count()
        
        edu_comments2 = [r.education_system for r in reviews2 if r.education_system][:3]
        staff_comments2 = [r.staff_review for r in reviews2 if r.staff_review][:3]
        infra_comments2 = [r.infrastructure_review for r in reviews2 if r.infrastructure_review][:3]
        placement_comments2 = [r.placement_review for r in reviews2 if r.placement_review][:3]
        fees_comments2 = [r.fees_structure for r in reviews2 if r.fees_structure][:3]
        
        comparison_data = {
            'college1': {
                'name': college1_name,
                'avg_overall': round(stats1['avg_overall'] or 0.0, 1),
                'avg_placement': round(stats1['avg_placement'] or 0.0, 1),
                'review_count': stats1['review_count'],
                'canteen_pct': round((canteen_yes1 / total_count1) * 100, 0),
                'hostel_pct': round((hostel_yes1 / total_count1) * 100, 0),
                'edu_comments': edu_comments1,
                'staff_comments': staff_comments1,
                'infra_comments': infra_comments1,
                'placement_comments': placement_comments1,
                'fees_comments': fees_comments1,
            },
            'college2': {
                'name': college2_name,
                'avg_overall': round(stats2['avg_overall'] or 0.0, 1),
                'avg_placement': round(stats2['avg_placement'] or 0.0, 1),
                'review_count': stats2['review_count'],
                'canteen_pct': round((canteen_yes2 / total_count2) * 100, 0),
                'hostel_pct': round((hostel_yes2 / total_count2) * 100, 0),
                'edu_comments': edu_comments2,
                'staff_comments': staff_comments2,
                'infra_comments': infra_comments2,
                'placement_comments': placement_comments2,
                'fees_comments': fees_comments2,
            }
        }
        
    context = {
        'college_names': college_names,
        'college1_name': college1_name,
        'college2_name': college2_name,
        'comparison_data': comparison_data
    }
    
    return render(request, 'app/compare.html', context)


# ═══════════════════════════════════════════════════════════════
#  FORGOT PASSWORD — Step 1: Enter Mobile Number
# ═══════════════════════════════════════════════════════════════
from .models import PasswordResetOTP, UserProfile
from .sms_service import send_otp_sms
from django.utils import timezone
from datetime import timedelta

def forgot_password(request):
    """
    Step 1: User submits their registered mobile number.
    If found, generate OTP, save to DB, send via SMS, redirect to verify step.
    """
    if request.method == 'POST':
        mobile = request.POST.get('mobile', '').strip()

        if not mobile:
            messages.error(request, 'Please enter a mobile number.')
            return render(request, 'app/forgot_password.html')

        # Rate-limit: no more than 3 OTP requests per mobile per 10 minutes
        ten_min_ago = timezone.now() - timedelta(minutes=10)
        recent_count = PasswordResetOTP.objects.filter(
            mobile=mobile, created_at__gte=ten_min_ago
        ).count()
        if recent_count >= 3:
            messages.error(request, 'Too many OTP requests. Please wait 10 minutes before trying again.')
            return render(request, 'app/forgot_password.html')

        # Look up user by mobile stored in UserProfile
        try:
            profile = UserProfile.objects.get(phone=mobile)
            user = profile.user
        except UserProfile.DoesNotExist:
            messages.error(request, 'No account found with this mobile number. Please check and try again.')
            return render(request, 'app/forgot_password.html')

        # Invalidate any previous unused OTPs for this mobile
        PasswordResetOTP.objects.filter(mobile=mobile, is_used=False).update(is_used=True)

        # Generate and store OTP
        otp_code = PasswordResetOTP.generate_otp()
        otp_obj  = PasswordResetOTP.objects.create(user=user, mobile=mobile, otp_code=otp_code)

        # Send SMS
        result = send_otp_sms(mobile, otp_code)
        if not result.get('success'):
            messages.error(request, 'Failed to send OTP. Please try again.')
            otp_obj.is_used = True
            otp_obj.save()
            return render(request, 'app/forgot_password.html')

        # Store OTP id in session (never the code itself)
        request.session['reset_otp_id'] = otp_obj.pk
        request.session['reset_mobile']  = mobile

        messages.success(request, f'OTP sent to {mobile[:4]}****{mobile[-3:]}. Valid for 5 minutes.')
        return redirect('verify_otp')

    return render(request, 'app/forgot_password.html')


# ═══════════════════════════════════════════════════════════════
#  FORGOT PASSWORD — Step 2: Verify OTP
# ═══════════════════════════════════════════════════════════════
def verify_otp(request):
    """
    Step 2: User enters the 6-digit OTP received on their phone.
    Validates correctness, expiry, and usage. On success, mark verified
    and allow the user to proceed to the password reset step.
    """
    otp_id = request.session.get('reset_otp_id')
    mobile = request.session.get('reset_mobile')

    if not otp_id or not mobile:
        messages.error(request, 'Session expired. Please start again.')
        return redirect('forgot_password')

    try:
        otp_obj = PasswordResetOTP.objects.get(pk=otp_id)
    except PasswordResetOTP.DoesNotExist:
        messages.error(request, 'Invalid session. Please start again.')
        return redirect('forgot_password')

    if request.method == 'POST':
        entered = request.POST.get('otp', '').strip()

        # Brute-force guard
        if otp_obj.attempts >= PasswordResetOTP.MAX_ATTEMPTS:
            messages.error(request, 'Too many incorrect attempts. Please request a new OTP.')
            return redirect('forgot_password')

        if otp_obj.is_expired:
            messages.error(request, 'OTP has expired. Please request a new one.')
            return redirect('forgot_password')

        if otp_obj.is_used:
            messages.error(request, 'This OTP has already been used. Please request a new one.')
            return redirect('forgot_password')

        otp_obj.attempts += 1

        if otp_obj.otp_code != entered:
            otp_obj.save()
            remaining = PasswordResetOTP.MAX_ATTEMPTS - otp_obj.attempts
            if remaining > 0:
                messages.error(request, f'Incorrect OTP. {remaining} attempt(s) remaining.')
            else:
                messages.error(request, 'Maximum attempts reached. Please request a new OTP.')
                return redirect('forgot_password')
            return render(request, 'app/verify_otp.html', {'mobile': mobile})

        # Correct OTP
        otp_obj.is_verified = True
        otp_obj.save()
        request.session['reset_otp_verified'] = True
        messages.success(request, 'OTP verified! Please set your new password.')
        return redirect('reset_password')

    seconds_left = max(0, int((otp_obj.expires_at - timezone.now()).total_seconds()))
    return render(request, 'app/verify_otp.html', {
        'mobile':       mobile,
        'seconds_left': seconds_left,
    })


# ═══════════════════════════════════════════════════════════════
#  FORGOT PASSWORD — Step 3: Set New Password
# ═══════════════════════════════════════════════════════════════
def reset_password(request):
    """
    Step 3: User sets a new password. Only accessible after OTP is verified.
    Invalidates the OTP after successful reset.
    """
    otp_id   = request.session.get('reset_otp_id')
    verified = request.session.get('reset_otp_verified')

    if not otp_id or not verified:
        messages.error(request, 'Unauthorised access. Please verify your OTP first.')
        return redirect('forgot_password')

    try:
        otp_obj = PasswordResetOTP.objects.get(pk=otp_id, is_verified=True, is_used=False)
    except PasswordResetOTP.DoesNotExist:
        messages.error(request, 'Invalid or expired session. Please start again.')
        return redirect('forgot_password')

    if request.method == 'POST':
        new_password     = request.POST.get('new_password1', '')
        confirm_password = request.POST.get('new_password2', '')

        # Validations
        if len(new_password) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return render(request, 'app/reset_password.html')
        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'app/reset_password.html')

        # Update password securely
        user = otp_obj.user
        user.set_password(new_password)
        user.save()

        # Mark OTP as fully used
        otp_obj.is_used = True
        otp_obj.save()

        # Clear reset session keys
        for key in ('reset_otp_id', 'reset_mobile', 'reset_otp_verified'):
            request.session.pop(key, None)

        messages.success(request, 'Password reset successfully! Please log in with your new password.')
        return redirect('login')

    return render(request, 'app/reset_password.html')


# ═══════════════════════════════════════════════════════════════
#  RESEND OTP helper
# ═══════════════════════════════════════════════════════════════
def resend_otp(request):
    """
    Resend a fresh OTP to the same mobile. Invalidates the old OTP.
    """
    mobile = request.session.get('reset_mobile')
    if not mobile:
        messages.error(request, 'Session expired. Please start again.')
        return redirect('forgot_password')

    # Rate-limit
    ten_min_ago  = timezone.now() - timedelta(minutes=10)
    recent_count = PasswordResetOTP.objects.filter(mobile=mobile, created_at__gte=ten_min_ago).count()
    if recent_count >= 3:
        messages.error(request, 'Too many OTP requests. Please wait 10 minutes.')
        return redirect('verify_otp')

    try:
        profile = UserProfile.objects.get(phone=mobile)
        user    = profile.user
    except UserProfile.DoesNotExist:
        return redirect('forgot_password')

    # Invalidate old OTPs
    PasswordResetOTP.objects.filter(mobile=mobile, is_used=False).update(is_used=True)

    # New OTP
    otp_code = PasswordResetOTP.generate_otp()
    otp_obj  = PasswordResetOTP.objects.create(user=user, mobile=mobile, otp_code=otp_code)
    result   = send_otp_sms(mobile, otp_code)

    if result.get('success'):
        request.session['reset_otp_id'] = otp_obj.pk
        messages.success(request, 'New OTP sent! Check your phone.')
    else:
        otp_obj.is_used = True
        otp_obj.save()
        messages.error(request, 'Failed to send OTP. Please try again.')

    return redirect('verify_otp')