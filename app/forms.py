from django import forms
from .models import CollegeReview

class CollegeReviewForm(forms.ModelForm):
    class Meta:
        model = CollegeReview
        fields = '__all__'
        exclude = ['user']
        
        widgets = {
            'college_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'required': True,
                'placeholder': 'Enter college/institute name'
            }),
            'user_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'readonly': True
            }),
            'mobile_number': forms.TextInput(attrs={
                'class': 'form-control', 
                'required': True,
                'placeholder': 'Enter your mobile number'
            }),
            'education_system': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4,
                'placeholder': 'Describe curriculum quality, teaching methods, academic resources, etc.'
            }),
            'staff_review': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4,
                'placeholder': 'Describe faculty qualifications, teaching quality, administrative support, etc.'
            }),
            'practical_experience': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4,
                'placeholder': 'Describe labs, workshops, internships, industry exposure, etc.'
            }),
            'fees_structure': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4,
                'placeholder': 'Describe tuition fees, additional charges, payment options, scholarships, etc.'
            }),
            'management_review': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4,
                'placeholder': 'Describe management responsiveness, policies, student support, etc.'
            }),
            'sports_cultural': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4,
                'placeholder': 'Describe available sports facilities, cultural events, clubs, etc.'
            }),
            'placement_review': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4,
                'placeholder': 'Describe placement statistics, companies visiting, career support, etc.'
            }),
            'placement_rating': forms.HiddenInput(),
            'travel_expense': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4,
                'placeholder': 'Describe transportation options, costs, commute time, etc.'
            }),
            'entrepreneurship_support': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4,
                'placeholder': 'Describe incubation centers, startup support, mentorship, etc.'
            }),
            'canteen_available': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'canteen_review': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3,
                'placeholder': 'Describe food quality, variety, hygiene, pricing, etc.'
            }),
            'hostel_available': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'hostel_review': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4,
                'placeholder': 'Describe rooms, amenities, food, rules, etc.'
            }),
            'infrastructure_review': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4,
                'placeholder': 'Describe buildings, classrooms, labs, library, wifi, etc.'
            }),
            'security_review': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4,
                'placeholder': 'Describe campus security, CCTV, emergency protocols, etc.'
            }),
            'overall_rating': forms.HiddenInput(attrs={
                'required': True
            }),
            'overall_review': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4, 
                'required': True,
                'placeholder': 'Provide your overall review and recommendations'
            }),
        }

from django.contrib.auth.models import User

class UserUpdateForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        # Ensure the new username isn't already taken by someone else
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'bio', 'phone', 'location', 'birth_date']
        widgets = {
            'profile_picture': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*', 'id': 'id_profile_picture'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Tell us something about yourself...'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City, Country'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def clean_profile_picture(self):
        picture = self.cleaned_data.get('profile_picture', False)
        if picture:
            if hasattr(picture, 'size'):
                if picture.size > 5 * 1024 * 1024:
                    raise forms.ValidationError("Image file too large ( > 5mb ).")
            
            if hasattr(picture, 'content_type'):
                if picture.content_type not in ['image/jpeg', 'image/png']:
                    raise forms.ValidationError("Unsupported file format. Please upload JPG, JPEG, or PNG.")
        return picture