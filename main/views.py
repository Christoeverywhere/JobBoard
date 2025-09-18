from django.shortcuts import render
from django.db.models import Count
from jobs.models import Job, JobCategory
from jobs.forms import JobSearchForm

def home(request):
    # Get recent jobs
    recent_jobs = Job.objects.filter(is_active=True)[:6]
    
    # Get job categories with job counts
    categories = JobCategory.objects.annotate(job_count=Count('job')).filter(job_count__gt=0)
    
    # Get job statistics
    total_jobs = Job.objects.filter(is_active=True).count()
    total_companies = Job.objects.filter(is_active=True).values('company').distinct().count()
    
    # Initialize search form
    search_form = JobSearchForm()
    
    context = {
        'recent_jobs': recent_jobs,
        'categories': categories,
        'total_jobs': total_jobs,
        'total_companies': total_companies,
        'search_form': search_form,
    }
    return render(request, 'main/home.html', context)

def about(request):
    return render(request, 'main/about.html')

def contact(request):
    if request.method == 'POST':
        # Handle contact form submission
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        # In a real application, you would save this to a database or send an email
        return render(request, 'main/contact_success.html', {'name': name})
    
    return render(request, 'main/contact.html')
