import re
from django import forms
from django.core.exceptions import ValidationError
from .models import Company, JobPosting, Candidate, JobApplication


class JobApplicationForm(forms.Form):
    job_id = forms.IntegerField(widget=forms.HiddenInput())
    full_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "e.g. Jane Doe",
            "required": True,
            "id": "app_full_name"
        }),
        label="Full Name"
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "e.g. jane.doe@example.com",
            "required": True,
            "id": "app_email"
        }),
        label="Email Address"
    )
    phone = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "e.g. +1 (555) 019-2834",
            "required": True,
            "id": "app_phone"
        }),
        label="Phone Number"
    )
    portfolio_url = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            "class": "form-control",
            "placeholder": "e.g. https://github.com/janedoe or portfolio link",
            "id": "app_portfolio_url"
        }),
        label="Portfolio / GitHub / LinkedIn (Optional)"
    )
    skills = forms.CharField(
        max_length=300,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "e.g. Python, Django, JavaScript, React, Docker",
            "required": True,
            "id": "app_skills"
        }),
        label="Skills & Expertise"
    )
    cover_letter = forms.CharField(
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 4,
            "placeholder": "Explain why you are an ideal fit for this position, highlighting key experiences and achievements...",
            "required": True,
            "id": "app_cover_letter"
        }),
        label="Cover Letter / Introduction"
    )

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "").strip()
        # Clean digits count
        digits = re.sub(r"\D", "", phone)
        if len(digits) < 7 or len(digits) > 15:
            raise ValidationError("Please provide a valid phone number (between 7 and 15 digits).")
        return phone

    def clean_full_name(self):
        full_name = self.cleaned_data.get("full_name", "").strip()
        if len(full_name) < 2:
            raise ValidationError("Full name must be at least 2 characters.")
        return full_name

    def clean_skills(self):
        skills = self.cleaned_data.get("skills", "").strip()
        if not skills:
            raise ValidationError("Please list at least one skill.")
        return skills

    def clean(self):
        cleaned_data = super().clean()
        job_id = cleaned_data.get("job_id")
        email = cleaned_data.get("email")

        if not job_id:
            raise ValidationError("Job posting identifier is missing.")

        try:
            job = JobPosting.objects.get(pk=job_id)
            cleaned_data["job_instance"] = job
        except JobPosting.DoesNotExist:
            raise ValidationError("The requested job posting does not exist.")

        if not job.active:
            raise ValidationError("This job posting is no longer accepting applications.")

        # Business logic: Prevent duplicate application by candidate email for the same job
        if email:
            email = email.lower().strip()
            existing_candidate = Candidate.objects.filter(email__iexact=email).first()
            if existing_candidate:
                if JobApplication.objects.filter(job=job, candidate=existing_candidate).exists():
                    raise ValidationError(
                        f"You have already submitted an application for '{job.title}' with this email ({email})."
                    )

        return cleaned_data

    def save(self):
        cleaned_data = self.cleaned_data
        job = cleaned_data["job_instance"]
        email = cleaned_data["email"].lower().strip()
        full_name = cleaned_data["full_name"]
        phone = cleaned_data["phone"]
        portfolio_url = cleaned_data.get("portfolio_url", "")
        skills = cleaned_data["skills"]
        cover_letter = cleaned_data["cover_letter"]

        # Get or create candidate
        candidate, created = Candidate.objects.get_or_create(
            email=email,
            defaults={
                "full_name": full_name,
                "phone": phone,
                "portfolio_url": portfolio_url,
                "skills": skills,
            }
        )

        # Update candidate info if existing
        if not created:
            candidate.full_name = full_name
            candidate.phone = phone
            if portfolio_url:
                candidate.portfolio_url = portfolio_url
            candidate.skills = skills
            candidate.save()

        # Create application
        application = JobApplication.objects.create(
            job=job,
            candidate=candidate,
            cover_letter=cover_letter,
            status=JobApplication.STATUS_APPLIED
        )
        return application


class JobPostingForm(forms.ModelForm):
    class Meta:
        model = JobPosting
        fields = [
            "company",
            "title",
            "job_type",
            "required_skills",
            "salary_range",
            "description",
            "active",
        ]
        widgets = {
            "company": forms.Select(attrs={"class": "form-select", "id": "id_company"}),
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Senior Backend Engineer", "id": "id_title"}),
            "job_type": forms.Select(attrs={"class": "form-select", "id": "id_job_type"}),
            "required_skills": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Python, Django, PostgreSQL, Celery", "id": "id_required_skills"}),
            "salary_range": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. $110,000 - $140,000 / year", "id": "id_salary_range"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 5, "placeholder": "Describe role responsibilities, tech stack, and benefits...", "id": "id_description"}),
            "active": forms.CheckboxInput(attrs={"class": "form-check-input", "id": "id_active"}),
        }


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ["name", "website", "location", "logo_url"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Stripe, TechNova Labs", "id": "id_company_name"}),
            "website": forms.URLInput(attrs={"class": "form-control", "placeholder": "e.g. https://example.com", "id": "id_company_website"}),
            "location": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. San Francisco, CA or Remote", "id": "id_company_location"}),
            "logo_url": forms.URLInput(attrs={"class": "form-control", "placeholder": "e.g. https://images.unsplash.com/... or company logo link", "id": "id_company_logo"}),
        }
