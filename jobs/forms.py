from django import forms
from .models import Job, JobApplication, JobCategory

class JobPostForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            'title', 'category', 'description', 'requirements', 'job_type', 
            'experience_level', 'salary_min', 'salary_max', 'location', 
            'remote_work', 'skills_required', 'application_deadline'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Describe the job role, responsibilities, and what makes this position exciting...'}),
            'requirements': forms.Textarea(attrs={'rows': 4, 'placeholder': 'List the required qualifications, experience, and skills...'}),
            'skills_required': forms.Textarea(attrs={'rows': 2, 'placeholder': 'e.g., Python, Django, JavaScript, React, SQL'}),
            'application_deadline': forms.DateInput(attrs={'type': 'date'}),
            'salary_min': forms.NumberInput(attrs={'placeholder': 'Minimum salary'}),
            'salary_max': forms.NumberInput(attrs={'placeholder': 'Maximum salary'}),
            'location': forms.TextInput(attrs={'placeholder': 'e.g., New York, NY or Remote'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].empty_label = "Select a category"
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['cover_letter']
        widgets = {
            'cover_letter': forms.Textarea(attrs={
                'rows': 6, 
                'placeholder': 'Write a compelling cover letter explaining why you are the perfect fit for this position...',
                'class': 'form-control'
            })
        }

class JobSearchForm(forms.Form):
    query = forms.CharField(
        max_length=200, 
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search jobs by title, company, or keywords...',
            'class': 'form-control'
        })
    )
    category = forms.ModelChoiceField(
        queryset=JobCategory.objects.all(),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    job_type = forms.ChoiceField(
        choices=[('', 'All Types')] + list(Job.JOB_TYPES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    experience_level = forms.ChoiceField(
        choices=[('', 'All Levels')] + list(Job.EXPERIENCE_LEVELS),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    location = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Location...',
            'class': 'form-control'
        })
    )
    remote_work = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    salary_min = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Min salary',
            'class': 'form-control'
        })
    )

class JobCategoryForm(forms.ModelForm):
    class Meta:
        model = JobCategory
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }