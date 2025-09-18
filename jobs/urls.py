from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    # Job listing and details
    path('', views.job_list, name='job_list'),
    path('<int:job_id>/', views.job_detail, name='job_detail'),
    
    # Job management (Employer)
    path('post/', views.post_job, name='post_job'),
    path('<int:job_id>/edit/', views.edit_job, name='edit_job'),
    path('<int:job_id>/delete/', views.delete_job, name='delete_job'),
    path('<int:job_id>/toggle-status/', views.toggle_job_status, name='toggle_job_status'),
    path('my-jobs/', views.my_jobs, name='my_jobs'),
    path('<int:job_id>/applications/', views.job_applications, name='job_applications'),
    
    # Job seeker actions
    path('<int:job_id>/apply/', views.apply_job, name='apply_job'),
    path('<int:job_id>/save/', views.save_job, name='save_job'),
    path('<int:job_id>/unsave/', views.unsave_job, name='unsave_job'),
    path('saved/', views.saved_jobs, name='saved_jobs'),
    path('my-applications/', views.my_applications, name='my_applications'),
]