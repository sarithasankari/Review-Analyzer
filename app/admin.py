from django.contrib import admin
from .models import CollegeReview

@admin.register(CollegeReview)
class CollegeReviewAdmin(admin.ModelAdmin):
    list_display = ['college_name', 'user_name', 'overall_rating', 'created_at']
    list_filter = ['overall_rating', 'created_at', 'canteen_available', 'hostel_available']
    search_fields = ['college_name', 'user_name', 'overall_review']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 20

from .models import ReviewComment
@admin.register(ReviewComment)
class ReviewCommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'review', 'created_at']
    search_fields = ['user__username', 'text']