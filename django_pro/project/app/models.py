from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class CollegeReview(models.Model):
    # College Information
    college_name = models.CharField(max_length=255)
    
    # Personal Information
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_name = models.CharField(max_length=255)
    mobile_number = models.CharField(max_length=15)
    
    # Review Sections
    education_system = models.TextField(blank=True, null=True)
    staff_review = models.TextField(blank=True, null=True)
    practical_experience = models.TextField(blank=True, null=True)
    fees_structure = models.TextField(blank=True, null=True)
    management_review = models.TextField(blank=True, null=True)
    sports_cultural = models.TextField(blank=True, null=True)
    placement_review = models.TextField(blank=True, null=True)
    placement_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        blank=True, 
        null=True
    )
    travel_expense = models.TextField(blank=True, null=True)
    entrepreneurship_support = models.TextField(blank=True, null=True)
    canteen_available = models.BooleanField(default=False)
    canteen_review = models.TextField(blank=True, null=True)
    hostel_available = models.BooleanField(default=False)
    hostel_review = models.TextField(blank=True, null=True)
    infrastructure_review = models.TextField(blank=True, null=True)
    security_review = models.TextField(blank=True, null=True)
    
    # Overall Rating
    overall_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    overall_review = models.TextField()
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Interactions
    likes = models.ManyToManyField(User, related_name='liked_reviews', blank=True)
    saves = models.ManyToManyField(User, related_name='saved_reviews', blank=True)
    
    class Meta:
        db_table = 'college_reviews'
        ordering = ['-created_at']
        verbose_name = 'College Review'
        verbose_name_plural = 'College Reviews'
    
    def __str__(self):
        return f"{self.college_name} - {self.user_name} ({self.overall_rating}/5)"

    @property
    def sentiment(self):
        if self.overall_rating >= 4:
            return 'Positive'
        elif self.overall_rating <= 2:
            return 'Negative'
        return 'Neutral'

from django.core.exceptions import ValidationError

def validate_image_size(image):
    limit_kb = 500
    if image.size > limit_kb * 1024:
        raise ValidationError(f"Image size must be less than {limit_kb} KB.")

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_images/', blank=True, null=True, max_length=500, validators=[validate_image_size])
    bio = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)


    def __str__(self):
        return f'{self.user.username} Profile'

class ReviewComment(models.Model):
    review = models.ForeignKey(CollegeReview, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    likes = models.ManyToManyField(User, related_name='liked_comments', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'review_comments'
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.user.username} on {self.review.college_name}"


import random
import string
from django.utils import timezone
from datetime import timedelta

class PasswordResetOTP(models.Model):
    """
    Stores a one-time password for mobile-based account recovery.
    Expires after 5 minutes. Supports attempt tracking and single use.
    """
    user        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_otps')
    mobile      = models.CharField(max_length=20)
    otp_code    = models.CharField(max_length=6)
    created_at  = models.DateTimeField(auto_now_add=True)
    expires_at  = models.DateTimeField()
    is_verified = models.BooleanField(default=False)   # True after OTP verified
    is_used     = models.BooleanField(default=False)   # True after password reset
    attempts    = models.PositiveSmallIntegerField(default=0)

    OTP_EXPIRY_MINUTES = 5
    MAX_ATTEMPTS       = 5

    class Meta:
        db_table  = 'password_reset_otps'
        ordering  = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.pk:
            self.expires_at = timezone.now() + timedelta(minutes=self.OTP_EXPIRY_MINUTES)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    @property
    def is_valid(self):
        return not self.is_expired and not self.is_used and self.attempts < self.MAX_ATTEMPTS

    @classmethod
    def generate_otp(cls):
        return ''.join(random.choices(string.digits, k=6))

    def __str__(self):
        return f"OTP for {self.user.username} | Expires: {self.expires_at} | Used: {self.is_used}"