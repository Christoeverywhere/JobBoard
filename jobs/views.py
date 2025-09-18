from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from accounts.models import UserProfile, EmployerProfile, JobSeekerProfile
from .models import Job, JobApplication, JobCategory, SavedJob
from .forms import JobPostForm, JobApplicationForm, JobSearchForm

def job_list(request):
    jobs = Job.objects.filter(is_active=True)
    form = JobSearchForm(request.GET)
    
    if form.is_valid():
        query = form.cleaned_data.get('query')
        category = form.cleaned_data.get('category')
        job_type = form.cleaned_data.get('job_type')
        experience_level = form.cleaned_data.get('experience_level')
        location = form.cleaned_data.get('location')
        remote_work = form.cleaned_data.get('remote_work')
        salary_min = form.cleaned_data.get('salary_min')
        
        if query:
            jobs = jobs.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(company__company_name__icontains=query) |
                Q(skills_required__icontains=query)
            )
        
        if category:
            jobs = jobs.filter(category=category)
        
        if job_type:
            jobs = jobs.filter(job_type=job_type)
        
        if experience_level:
            jobs = jobs.filter(experience_level=experience_level)
        
        if location:
            jobs = jobs.filter(location__icontains=location)
        
        if remote_work:
            jobs = jobs.filter(remote_work=True)
        
        if salary_min:
            jobs = jobs.filter(salary_min__gte=salary_min)
    
    # Pagination
    paginator = Paginator(jobs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'form': form,
        'total_jobs': jobs.count()
    }
    return render(request, 'jobs/job_list.html', context)

def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id, is_active=True)
    
    # Check if user has applied
    has_applied = False
    is_saved = False
    can_apply = False
    
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            if user_profile.user_type == 'job_seeker':
                jobseeker_profile = JobSeekerProfile.objects.get(user_profile=user_profile)
                has_applied = JobApplication.objects.filter(job=job, applicant=jobseeker_profile).exists()
                is_saved = SavedJob.objects.filter(job=job, job_seeker=jobseeker_profile).exists()
                can_apply = True
        except (UserProfile.DoesNotExist, JobSeekerProfile.DoesNotExist):
            pass
    
    context = {
        'job': job,
        'has_applied': has_applied,
        'is_saved': is_saved,
        'can_apply': can_apply
    }
    return render(request, 'jobs/job_detail.html', context)

@login_required
def post_job(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.user_type != 'employer':
            messages.error(request, 'Only employers can post jobs.')
            return redirect('jobs:job_list')
        
        employer_profile = EmployerProfile.objects.get(user_profile=user_profile)
    except (UserProfile.DoesNotExist, EmployerProfile.DoesNotExist):
        messages.error(request, 'Please complete your employer profile first.')
        return redirect('accounts:profile')
    
    if request.method == 'POST':
        form = JobPostForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.company = employer_profile
            job.save()
            messages.success(request, 'Job posted successfully!')
            return redirect('jobs:job_detail', job_id=job.id)
    else:
        form = JobPostForm()
    
    return render(request, 'jobs/post_job.html', {'form': form})

@login_required
def apply_job(request, job_id):
    job = get_object_or_404(Job, id=job_id, is_active=True)
    
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.user_type != 'job_seeker':
            messages.error(request, 'Only job seekers can apply for jobs.')
            return redirect('jobs:job_detail', job_id=job_id)
        
        jobseeker_profile = JobSeekerProfile.objects.get(user_profile=user_profile)
    except (UserProfile.DoesNotExist, JobSeekerProfile.DoesNotExist):
        messages.error(request, 'Please complete your job seeker profile first.')
        return redirect('accounts:profile')
    
    # Check if already applied
    if JobApplication.objects.filter(job=job, applicant=jobseeker_profile).exists():
        messages.warning(request, 'You have already applied for this job.')
        return redirect('jobs:job_detail', job_id=job_id)
    
    if request.method == 'POST':
        form = JobApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = jobseeker_profile
            application.save()
            messages.success(request, 'Application submitted successfully!')
            return redirect('jobs:job_detail', job_id=job_id)
    else:
        form = JobApplicationForm()
    
    return render(request, 'jobs/apply_job.html', {'form': form, 'job': job})

@login_required
def my_jobs(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        
        if user_profile.user_type == 'employer':
            employer_profile = EmployerProfile.objects.get(user_profile=user_profile)
            jobs = Job.objects.filter(company=employer_profile).order_by('-created_at')
            return render(request, 'jobs/my_jobs_employer.html', {'jobs': jobs})
        
        elif user_profile.user_type == 'job_seeker':
            jobseeker_profile = JobSeekerProfile.objects.get(user_profile=user_profile)
            applications = JobApplication.objects.filter(applicant=jobseeker_profile).order_by('-applied_at')
            saved_jobs = SavedJob.objects.filter(job_seeker=jobseeker_profile).order_by('-saved_at')
            return render(request, 'jobs/my_jobs_jobseeker.html', {
                'applications': applications,
                'saved_jobs': saved_jobs
            })
    
    except (UserProfile.DoesNotExist, EmployerProfile.DoesNotExist, JobSeekerProfile.DoesNotExist):
        messages.error(request, 'Please complete your profile first.')
        return redirect('accounts:profile')

@login_required
def save_job(request, job_id):
    job = get_object_or_404(Job, id=job_id, is_active=True)
    
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.user_type != 'job_seeker':
            messages.error(request, 'Only job seekers can save jobs.')
            return redirect('jobs:job_detail', job_id=job_id)
        
        jobseeker_profile = JobSeekerProfile.objects.get(user_profile=user_profile)
    except (UserProfile.DoesNotExist, JobSeekerProfile.DoesNotExist):
        messages.error(request, 'Please complete your job seeker profile first.')
        return redirect('accounts:profile')
    
    saved_job, created = SavedJob.objects.get_or_create(job=job, job_seeker=jobseeker_profile)
    
    if created:
        messages.success(request, 'Job saved successfully!')
    else:
        messages.info(request, 'Job is already in your saved list.')
    
    return redirect('jobs:job_detail', job_id=job_id)

@login_required
def unsave_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        jobseeker_profile = JobSeekerProfile.objects.get(user_profile=user_profile)
        
        saved_job = SavedJob.objects.get(job=job, job_seeker=jobseeker_profile)
        saved_job.delete()
        messages.success(request, 'Job removed from saved list.')
    except (UserProfile.DoesNotExist, JobSeekerProfile.DoesNotExist, SavedJob.DoesNotExist):
        messages.error(request, 'Job not found in your saved list.')
    
    return redirect('jobs:job_detail', job_id=job_id)

@login_required
def job_applications(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        employer_profile = EmployerProfile.objects.get(user_profile=user_profile)
        
        # Check if the employer owns this job
        if job.company != employer_profile:
            messages.error(request, 'You can only view applications for your own jobs.')
            return redirect('jobs:job_detail', job_id=job_id)
        
        applications = JobApplication.objects.filter(job=job).order_by('-applied_at')
        
        return render(request, 'jobs/job_applications.html', {
            'job': job,
            'applications': applications
        })
    
    except (UserProfile.DoesNotExist, EmployerProfile.DoesNotExist):
        messages.error(request, 'Access denied.')
        return redirect('jobs:job_detail', job_id=job_id)

@login_required
def edit_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        employer_profile = EmployerProfile.objects.get(user_profile=user_profile)
        
        # Check if the employer owns this job
        if job.company != employer_profile:
            messages.error(request, 'You can only edit your own jobs.')
            return redirect('jobs:job_detail', job_id=job_id)
        
        if request.method == 'POST':
            form = JobPostForm(request.POST, instance=job)
            if form.is_valid():
                form.save()
                messages.success(request, 'Job updated successfully!')
                return redirect('jobs:job_detail', job_id=job.id)
        else:
            form = JobPostForm(instance=job)
        
        return render(request, 'jobs/edit_job.html', {
            'form': form,
            'job': job
        })
    
    except (UserProfile.DoesNotExist, EmployerProfile.DoesNotExist):
        messages.error(request, 'Access denied.')
        return redirect('jobs:job_detail', job_id=job_id)

@login_required
def delete_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        employer_profile = EmployerProfile.objects.get(user_profile=user_profile)
        
        # Check if the employer owns this job
        if job.company != employer_profile:
            messages.error(request, 'You can only delete your own jobs.')
            return redirect('jobs:job_detail', job_id=job_id)
        
        if request.method == 'POST':
            job.delete()
            messages.success(request, 'Job deleted successfully!')
            return redirect('jobs:my_jobs')
        
        return render(request, 'jobs/delete_job_confirm.html', {'job': job})
    
    except (UserProfile.DoesNotExist, EmployerProfile.DoesNotExist):
        messages.error(request, 'Access denied.')
        return redirect('jobs:job_detail', job_id=job_id)

@login_required
def toggle_job_status(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        employer_profile = EmployerProfile.objects.get(user_profile=user_profile)
        
        # Check if the employer owns this job
        if job.company != employer_profile:
            messages.error(request, 'You can only modify your own jobs.')
            return redirect('jobs:job_detail', job_id=job_id)
        
        if request.method == 'POST':
            job.is_active = not job.is_active
            job.save()
            status = 'activated' if job.is_active else 'deactivated'
            messages.success(request, f'Job {status} successfully!')
        
        return redirect('jobs:my_jobs')
    
    except (UserProfile.DoesNotExist, EmployerProfile.DoesNotExist):
        messages.error(request, 'Access denied.')
        return redirect('jobs:job_detail', job_id=job_id)

@login_required
def saved_jobs(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.user_type != 'job_seeker':
            messages.error(request, 'Only job seekers can view saved jobs.')
            return redirect('jobs:job_list')
        
        jobseeker_profile = JobSeekerProfile.objects.get(user_profile=user_profile)
        saved_jobs_list = SavedJob.objects.filter(job_seeker=jobseeker_profile).order_by('-saved_at')
        
        # Pagination
        paginator = Paginator(saved_jobs_list, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        return render(request, 'jobs/saved_jobs.html', {
            'page_obj': page_obj,
            'total_saved': saved_jobs_list.count()
        })
    
    except (UserProfile.DoesNotExist, JobSeekerProfile.DoesNotExist):
        messages.error(request, 'Please complete your job seeker profile first.')
        return redirect('accounts:profile')

@login_required
def my_applications(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.user_type != 'job_seeker':
            messages.error(request, 'Only job seekers can view applications.')
            return redirect('jobs:job_list')
        
        jobseeker_profile = JobSeekerProfile.objects.get(user_profile=user_profile)
        applications = JobApplication.objects.filter(applicant=jobseeker_profile).order_by('-applied_at')
        
        # Pagination
        paginator = Paginator(applications, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        return render(request, 'jobs/my_applications.html', {
            'page_obj': page_obj,
            'total_applications': applications.count()
        })
    
    except (UserProfile.DoesNotExist, JobSeekerProfile.DoesNotExist):
        messages.error(request, 'Please complete your job seeker profile first.')
        return redirect('accounts:profile')
