from django.contrib import admin
from .models import CollegeReview

@admin.register(CollegeReview)
class CollegeReviewAdmin(admin.ModelAdmin):
    list_display = ('college_name', 'user_name', 'overall_rating', 'created_at')
    list_filter = ('overall_rating', 'created_at')
    search_fields = ('college_name', 'user_name')