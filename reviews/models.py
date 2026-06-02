# models.py
from django.db import models

class CollegeReview(models.Model):
    college_name = models.CharField(max_length=255)
    user_name = models.CharField(max_length=255)
    mobile_number = models.CharField(max_length=15)
    education_system = models.TextField(blank=True, default='')
    staff_review = models.TextField(blank=True, default='')
    practical_experience = models.TextField(blank=True, default='')
    fees_structure = models.TextField(blank=True, default='')
    management_review = models.TextField(blank=True, default='')
    sports_cultural = models.TextField(blank=True, default='')
    placement_review = models.TextField(blank=True, default='')
    placement_rating = models.IntegerField(null=True, blank=True)
    travel_expense = models.TextField(blank=True, default='')
    entrepreneurship_support = models.TextField(blank=True, default='')
    canteen_available = models.BooleanField(default=False)
    canteen_review = models.TextField(blank=True, default='')
    hostel_available = models.BooleanField(default=False)
    hostel_review = models.TextField(blank=True, default='')
    infrastructure_review = models.TextField(blank=True, default='')
    security_review = models.TextField(blank=True, default='')
    overall_rating = models.IntegerField()
    overall_review = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.college_name} - {self.user_name}"