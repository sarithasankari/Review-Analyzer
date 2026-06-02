from django.urls import path
from . import views

urlpatterns = [
    path('submit-review/', views.submit_review, name='submit_review'),
    path('view-data/', views.view_data, name='view_data'),
    path('show-data/', views.show_data, name='show_data'),
    path('review-form/', views.review_form_page, name='review_form'),
    path('debug/', views.debug_data, name='debug_data'),
    path('debug-db/', views.debug_database, name='debug_database'),
    path('check-migrations/', views.check_migrations, name='check_migrations'),
    path('check-db/', views.check_database_info, name='check_db'),
    path('check-database/', views.check_database, name='check_database'),
    path('export-data/', views.export_all_data, name='export_data'),
    path('save-data/', views.save_all_data, name='save_data'),
    path('all-data/', views.view_all_data_pretty, name='all_data'),
]