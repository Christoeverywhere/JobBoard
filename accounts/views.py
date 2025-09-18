from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import CustomUserCreationForm, EmployerProfileForm, JobSeekerProfileForm, UserProfileUpdateForm, UserUpdateForm
from .models import UserProfile, EmployerProfile, JobSeekerProfile

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            
            # Redirect to profile completion based on user type
            user_profile = UserProfile.objects.get(user=user)
            if user_profile.user_type == 'employer':
                return redirect('accounts:complete_employer_profile')
            else:
                return redirect('accounts:complete_jobseeker_profile')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def complete_employer_profile(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    if user_profile.user_type != 'employer':
        messages.error(request, 'Access denied.')
        return redirect('main:home')
    
    # Check if profile already exists
    try:
        employer_profile = EmployerProfile.objects.get(user_profile=user_profile)
        return redirect('accounts:profile')
    except EmployerProfile.DoesNotExist:
        pass
    
    if request.method == 'POST':
        form = EmployerProfileForm(request.POST)
        if form.is_valid():
            employer_profile = form.save(commit=False)
            employer_profile.user_profile = user_profile
            employer_profile.save()
            messages.success(request, 'Profile completed successfully!')
            return redirect('accounts:profile')
    else:
        form = EmployerProfileForm()
    
    return render(request, 'accounts/complete_employer_profile.html', {'form': form})

@login_required
def complete_jobseeker_profile(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    if user_profile.user_type != 'job_seeker':
        messages.error(request, 'Access denied.')
        return redirect('main:home')
    
    # Check if profile already exists
    try:
        jobseeker_profile = JobSeekerProfile.objects.get(user_profile=user_profile)
        return redirect('accounts:profile')
    except JobSeekerProfile.DoesNotExist:
        pass
    
    if request.method == 'POST':
        form = JobSeekerProfileForm(request.POST, request.FILES)
        if form.is_valid():
            jobseeker_profile = form.save(commit=False)
            jobseeker_profile.user_profile = user_profile
            jobseeker_profile.save()
            messages.success(request, 'Profile completed successfully!')
            return redirect('accounts:profile')
    else:
        form = JobSeekerProfileForm()
    
    return render(request, 'accounts/complete_jobseeker_profile.html', {'form': form})

@login_required
def profile(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    context = {'user_profile': user_profile}
    
    if user_profile.user_type == 'employer':
        try:
            employer_profile = EmployerProfile.objects.get(user_profile=user_profile)
            context['employer_profile'] = employer_profile
        except EmployerProfile.DoesNotExist:
            return redirect('accounts:complete_employer_profile')
    else:
        try:
            jobseeker_profile = JobSeekerProfile.objects.get(user_profile=user_profile)
            context['jobseeker_profile'] = jobseeker_profile
        except JobSeekerProfile.DoesNotExist:
            return redirect('accounts:complete_jobseeker_profile')
    
    return render(request, 'accounts/profile.html', context)

@login_required
def edit_profile(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileUpdateForm(request.POST, instance=user_profile)
        
        if user_profile.user_type == 'employer':
            try:
                employer_profile = EmployerProfile.objects.get(user_profile=user_profile)
                employer_form = EmployerProfileForm(request.POST, instance=employer_profile)
                
                if user_form.is_valid() and profile_form.is_valid() and employer_form.is_valid():
                    user_form.save()
                    profile_form.save()
                    employer_form.save()
                    messages.success(request, 'Profile updated successfully!')
                    return redirect('accounts:profile')
            except EmployerProfile.DoesNotExist:
                return redirect('accounts:complete_employer_profile')
        else:
            try:
                jobseeker_profile = JobSeekerProfile.objects.get(user_profile=user_profile)
                jobseeker_form = JobSeekerProfileForm(request.POST, request.FILES, instance=jobseeker_profile)
                
                if user_form.is_valid() and profile_form.is_valid() and jobseeker_form.is_valid():
                    user_form.save()
                    profile_form.save()
                    jobseeker_form.save()
                    messages.success(request, 'Profile updated successfully!')
                    return redirect('accounts:profile')
            except JobSeekerProfile.DoesNotExist:
                return redirect('accounts:complete_jobseeker_profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileUpdateForm(instance=user_profile)
        
        if user_profile.user_type == 'employer':
            try:
                employer_profile = EmployerProfile.objects.get(user_profile=user_profile)
                employer_form = EmployerProfileForm(instance=employer_profile)
                return render(request, 'accounts/edit_profile.html', {
                    'user_form': user_form,
                    'profile_form': profile_form,
                    'employer_form': employer_form,
                    'user_profile': user_profile
                })
            except EmployerProfile.DoesNotExist:
                return redirect('accounts:complete_employer_profile')
        else:
            try:
                jobseeker_profile = JobSeekerProfile.objects.get(user_profile=user_profile)
                jobseeker_form = JobSeekerProfileForm(instance=jobseeker_profile)
                return render(request, 'accounts/edit_profile.html', {
                    'user_form': user_form,
                    'profile_form': profile_form,
                    'jobseeker_form': jobseeker_form,
                    'user_profile': user_profile
                })
            except JobSeekerProfile.DoesNotExist:
                return redirect('accounts:complete_jobseeker_profile')
