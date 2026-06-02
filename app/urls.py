from django.urls import path
from . import views

urlpatterns = [
    # Main pages
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('compare/', views.compare_view, name='compare'),
    
    # Review-related URLs
    path('review/', views.review_form, name='review_form'),
    path('review-page/', views.review_page, name='review_page'),
    path('review-page/<str:college_name>/', views.review_page, name='review_page_with_college'),
    path('api/submit-review/', views.api_submit_review, name='api_submit_review'),
    path('review/success/', views.review_success, name='review_success'),
    path('reviews/', views.review_list, name='review_list'),
    path('reviews/<int:review_id>/', views.review_detail, name='review_detail'),
    path('reviews/institution/<str:college_name>/', views.view_reviews, name='view_reviews'),
    path('my-reviews/', views.get_user_reviews, name='my_reviews'),
    path('profile/', views.profile_view, name='profile'),
    path('settings/', views.settings_view, name='settings'),
    path('reviews/<int:review_id>/like/', views.toggle_like, name='toggle_like'),
    path('reviews/<int:review_id>/save/', views.toggle_save, name='toggle_save'),
    path('reviews/<int:review_id>/comment/', views.add_comment, name='add_comment'),
    path('comments/<int:comment_id>/like/', views.toggle_comment_like, name='toggle_comment_like'),
    path('simple/', views.simple_review_form, name='simple_form'),  # Fallback route

    # Forgot Password (OTP flow)
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),
]