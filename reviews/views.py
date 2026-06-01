from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import connection
from django.conf import settings
from django.db.migrations.executor import MigrationExecutor
from django.core.exceptions import ObjectDoesNotExist
import json
import os
from .models import CollegeReview


def view_data(request):
    """View to display data in template"""
    reviews = CollegeReview.objects.all().order_by('-created_at')
    return render(request, 'reviews/view_data.html', {'reviews': reviews})


def show_data(request):
    """Alternative view to display data"""
    reviews = CollegeReview.objects.all().order_by('-created_at')
    return render(request, 'reviews/show_data.html', {'reviews': reviews})


def review_form_page(request):
    """View to render the review form HTML page"""
    return render(request, 'reviews/review_form.html')


@csrf_exempt
@require_http_methods(["POST"])
def submit_review(request):
    """Handle form submission with better validation"""
    if request.method == 'POST':
        try:
            # Parse JSON data from the form
            data = json.loads(request.body)
            print("=== FORM DATA RECEIVED ===")
            print("Data:", data)
            
            # Validate required fields
            required_fields = ['college_name', 'user_name', 'mobile_number', 'overall_rating']
            missing_fields = [field for field in required_fields if not data.get(field)]
            
            if missing_fields:
                return JsonResponse({
                    'success': False,
                    'error': f'Missing required fields: {", ".join(missing_fields)}'
                }, status=400)
            
            # Convert and validate numeric fields
            try:
                placement_rating = int(data.get('placement_rating', 0)) if data.get('placement_rating') else None
                overall_rating = int(data['overall_rating'])
            except (ValueError, TypeError) as e:
                return JsonResponse({
                    'success': False,
                    'error': f'Invalid rating values: {str(e)}'
                }, status=400)
            
            # Handle boolean fields properly
            canteen_available = bool(data.get('canteen_available', False))
            hostel_available = bool(data.get('hostel_available', False))
            
            # Create and save the review
            review = CollegeReview(
                college_name=data['college_name'].strip(),
                user_name=data['user_name'].strip(),
                mobile_number=data['mobile_number'].strip(),
                education_system=data.get('education_system', '').strip(),
                staff_review=data.get('staff_review', '').strip(),
                practical_experience=data.get('practical_experience', '').strip(),
                fees_structure=data.get('fees_structure', '').strip(),
                management_review=data.get('management_review', '').strip(),
                sports_cultural=data.get('sports_cultural', '').strip(),
                placement_review=data.get('placement_review', '').strip(),
                placement_rating=placement_rating,
                travel_expense=data.get('travel_expense', '').strip(),
                entrepreneurship_support=data.get('entrepreneurship_support', '').strip(),
                canteen_available=canteen_available,
                canteen_review=data.get('canteen_review', '').strip(),
                hostel_available=hostel_available,
                hostel_review=data.get('hostel_review', '').strip(),
                infrastructure_review=data.get('infrastructure_review', '').strip(),
                security_review=data.get('security_review', '').strip(),
                overall_rating=overall_rating,
                overall_review=data.get('overall_review', '').strip(),
            )
            
            # Debug info
            print("=== REVIEW OBJECT BEFORE SAVE ===")
            print(f"ID: {review.id}")
            print(f"College: {review.college_name}")
            print(f"User: {review.user_name}")
            print(f"Mobile: {review.mobile_number}")
            print(f"Rating: {review.overall_rating}")
            
            review.save()
            
            print("=== AFTER SAVE ===")
            print(f"Review ID: {review.id}")
            print(f"Created at: {review.created_at}")
            
            # Verify the save worked
            saved_review = CollegeReview.objects.get(id=review.id)
            print(f"Verified - ID: {saved_review.id}, College: {saved_review.college_name}")
            
            return JsonResponse({
                'success': True,
                'message': 'Review submitted successfully!',
                'review_id': review.id,
                'college_name': review.college_name
            })
            
        except json.JSONDecodeError as e:
            return JsonResponse({
                'success': False,
                'error': f'Invalid JSON data: {str(e)}'
            }, status=400)
        except Exception as e:
            print("=== ERROR ===")
            print(f"Error type: {type(e).__name__}")
            print(f"Error details: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            
            return JsonResponse({
                'success': False,
                'error': f'{type(e).__name__}: {str(e)}'
            }, status=400)


def debug_data(request):
    """Debug view showing all data with database info"""
    reviews = CollegeReview.objects.all().order_by('-created_at')
    
    # Get ALL fields from all reviews
    all_reviews_data = list(reviews.values(
        'id', 'college_name', 'user_name', 'mobile_number', 
        'education_system', 'staff_review', 'practical_experience',
        'fees_structure', 'management_review', 'sports_cultural',
        'placement_review', 'placement_rating', 'travel_expense',
        'entrepreneurship_support', 'canteen_available', 'canteen_review',
        'hostel_available', 'hostel_review', 'infrastructure_review',
        'security_review', 'overall_rating', 'overall_review',
        'created_at', 'updated_at'
    ))
    
    context = {
        'db_engine': connection.settings_dict['ENGINE'],
        'db_name': connection.settings_dict['NAME'],
        'db_host': connection.settings_dict['HOST'],
        'reviews_count': reviews.count(),
        'reviews': all_reviews_data
    }
    
    return JsonResponse(context, json_dumps_params={'indent': 2})


def debug_database(request):
    """Comprehensive database debug information"""
    debug_info = {
        'database_engine': connection.settings_dict['ENGINE'],
        'database_name': connection.settings_dict['NAME'],
        'database_host': connection.settings_dict['HOST'],
        'database_user': connection.settings_dict['USER'],
        'reviews_count': CollegeReview.objects.count(),
        'tables': connection.introspection.table_names(),
    }
    
    # Test database operations
    try:
        # Create a test record
        test_review = CollegeReview(
            college_name="Test College Debug",
            user_name="Test User Debug",
            mobile_number="0000000000",
            overall_rating=5,
            overall_review="This is a test review for debugging"
        )
        test_review.save()
        debug_info['test_record_created'] = True
        debug_info['test_record_id'] = test_review.id
        
        # Try to retrieve it
        retrieved = CollegeReview.objects.get(id=test_review.id)
        debug_info['test_record_retrieved'] = True
        debug_info['retrieved_college_name'] = retrieved.college_name
        
        # Clean up
        test_review.delete()
        debug_info['test_record_deleted'] = True
        debug_info['final_count'] = CollegeReview.objects.count()
        
    except Exception as e:
        debug_info['test_error'] = str(e)
        debug_info['error_type'] = type(e).__name__
    
    return JsonResponse(debug_info, json_dumps_params={'indent': 2})


def check_migrations(request):
    """Check migration status"""
    executor = MigrationExecutor(connection)
    plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
    
    debug_info = {
        'migrations_pending': len(plan) > 0,
        'pending_migrations': [str(migration) for migration in plan],
        'applied_migrations_count': len(executor.loader.applied_migrations),
        'applied_migrations': list(executor.loader.applied_migrations),
    }
    
    return JsonResponse(debug_info, json_dumps_params={'indent': 2})


def check_database_info(request):
    """Basic database connection info"""
    db_info = connection.settings_dict
    
    return JsonResponse({
        'database_name': db_info['NAME'],
        'database_engine': db_info['ENGINE'],
        'database_user': db_info['USER'],
        'database_host': db_info['HOST'],
        'database_port': db_info['PORT'],
    }, json_dumps_params={'indent': 2})


def check_database(request):
    """Comprehensive database check"""
    db_info = {
        'configured_engine': settings.DATABASES['default']['ENGINE'],
        'configured_name': settings.DATABASES['default']['NAME'],
        'actual_database': connection.settings_dict['NAME'],
        'actual_engine': connection.settings_dict['ENGINE'],
    }
    
    # Test database connection and queries
    try:
        count = CollegeReview.objects.count()
        db_info['reviews_count'] = count
        db_info['database_working'] = True
        db_info['connection_status'] = 'Connected successfully'
        
        # Test raw SQL connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            db_info['mysql_version'] = cursor.fetchone()[0]
            
    except Exception as e:
        db_info['database_working'] = False
        db_info['connection_status'] = f'Failed: {str(e)}'
        db_info['error_type'] = type(e).__name__
    
    return JsonResponse(db_info, json_dumps_params={'indent': 2})


def export_all_data(request):
    """Export all data as downloadable JSON file"""
    all_data = list(CollegeReview.objects.all().values())
    
    if not all_data:
        return JsonResponse({
            'success': False,
            'message': 'No data available to export',
            'records_count': 0
        })
    
    # Create JSON response for download
    response = HttpResponse(
        json.dumps(all_data, indent=2, default=str, ensure_ascii=False),
        content_type='application/json; charset=utf-8'
    )
    response['Content-Disposition'] = 'attachment; filename="college_reviews_export.json"'
    
    return response


def save_all_data(request):
    """Save all data to a JSON file on the server"""
    all_data = list(CollegeReview.objects.all().values())
    
    if not all_data:
        return JsonResponse({
            'success': False,
            'message': 'No data available to save',
            'records_count': 0
        })
    
    # Save to file
    file_path = os.path.join(settings.BASE_DIR, 'college_reviews_backup.json')
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, indent=2, default=str, ensure_ascii=False)
        
        return JsonResponse({
            'success': True,
            'message': f'Data successfully saved to {file_path}',
            'records_saved': len(all_data),
            'file_path': file_path,
            'file_size': f"{os.path.getsize(file_path)} bytes"
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Failed to save file: {str(e)}',
            'error_type': type(e).__name__
        })


def view_all_data_pretty(request):
    """View all data in pretty formatted JSON"""
    reviews = CollegeReview.objects.all().order_by('-created_at')
    
    # Prepare data with all fields and proper formatting
    data = []
    for review in reviews:
        data.append({
            'id': review.id,
            'college_name': review.college_name,
            'user_name': review.user_name,
            'mobile_number': review.mobile_number,
            'education_system': review.education_system,
            'staff_review': review.staff_review,
            'practical_experience': review.practical_experience,
            'fees_structure': review.fees_structure,
            'management_review': review.management_review,
            'sports_cultural': review.sports_cultural,
            'placement_review': review.placement_review,
            'placement_rating': review.placement_rating,
            'travel_expense': review.travel_expense,
            'entrepreneurship_support': review.entrepreneurship_support,
            'canteen_available': review.canteen_available,
            'canteen_review': review.canteen_review,
            'hostel_available': review.hostel_available,
            'hostel_review': review.hostel_review,
            'infrastructure_review': review.infrastructure_review,
            'security_review': review.security_review,
            'overall_rating': review.overall_rating,
            'overall_review': review.overall_review,
            'created_at': review.created_at.strftime('%Y-%m-%d %H:%M:%S') if review.created_at else None,
            'updated_at': review.updated_at.strftime('%Y-%m-%d %H:%M:%S') if review.updated_at else None,
        })
    
    response_data = {
        'success': True,
        'total_records': len(data),
        'exported_at': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
        'reviews': data
    }
    
    return JsonResponse(response_data, json_dumps_params={'indent': 2})


# Add this import at the top if not already there
from django.utils import timezone