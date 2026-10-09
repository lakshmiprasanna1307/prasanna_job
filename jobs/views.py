import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q

from .models import Company, JobPosting, Candidate, JobApplication
from .forms import JobApplicationForm, JobPostingForm



def is_recruiter(user):
    return user.is_authenticated and user.is_staff


def job_list(request):
    """Active job listing page with live JavaScript search and filtering."""
    jobs = JobPosting.objects.filter(active=True).select_related("company")
    
    # Extract unique skills and locations for filter pills
    all_skills_set = set()
    for job in jobs:
        for s in job.skills_list():
            all_skills_set.add(s)
    skills_list = sorted(list(all_skills_set))[:20]

    locations = sorted(list(set(jobs.values_list("company__location", flat=True))))
    job_types = [choice[0] for choice in JobPosting.JOB_TYPE_CHOICES]

    application_form = JobApplicationForm()

    context = {
        "jobs": jobs,
        "skills_list": skills_list,
        "locations": locations,
        "job_types": job_types,
        "application_form": application_form,
        "total_jobs_count": jobs.count(),
    }
    return render(request, "jobs/job_list.html", context)


def job_detail(request, pk):
    """Job detail page showing company, requirements, salary, and application modal."""
    job = get_object_or_404(JobPosting.objects.select_related("company"), pk=pk)
    related_jobs = (
        JobPosting.objects.filter(active=True)
        .exclude(pk=job.pk)
        .filter(Q(company=job.company) | Q(job_type=job.job_type))
        .select_related("company")[:3]
    )
    application_form = JobApplicationForm(initial={"job_id": job.pk})

    context = {
        "job": job,
        "related_jobs": related_jobs,
        "application_form": application_form,
    }
    return render(request, "jobs/job_detail.html", context)


@require_POST
def apply_job(request):
    """
    Application submission workflow.
    Handles both AJAX/JSON requests and standard form submissions with CSRF protection.
    Prevents duplicate submissions by candidate email for the same job.
    """
    is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest" or request.content_type == "application/json"
    
    if request.content_type == "application/json":
        try:
            data = json.loads(request.body.decode("utf-8"))
            form = JobApplicationForm(data)
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Invalid JSON format payload."}, status=400)
    else:
        form = JobApplicationForm(request.POST)

    if form.is_valid():
        application = form.save()
        success_msg = f"Application submitted successfully for {application.job.title} at {application.job.company.name}!"
        if is_ajax:
            return JsonResponse({
                "success": True,
                "message": success_msg,
                "application_id": application.id,
                "candidate_name": application.candidate.full_name,
                "job_title": application.job.title,
                "status": application.status,
            })
        messages.success(request, success_msg)
        return redirect("job_detail", pk=application.job.pk)
    else:
        # Collect error messages
        errors = []
        for field, field_errors in form.errors.items():
            for err in field_errors:
                if field == "__all__":
                    errors.append(f"{err}")
                else:
                    errors.append(f"{form.fields[field].label or field}: {err}")
        
        error_msg = " ".join(errors)
        if is_ajax:
            return JsonResponse({
                "success": False,
                "error": error_msg,
                "field_errors": form.errors
            }, status=400)
        
        messages.error(request, error_msg)
        job_id = request.POST.get("job_id")
        if job_id:
            return redirect("job_detail", pk=job_id)
        return redirect("job_list")


@login_required(login_url="login")
@user_passes_test(is_recruiter, login_url="login")
def recruiter_dashboard(request):
    """
    Recruiter dashboard showing hiring pipeline stages:
    Applied, Under Review, Shortlisted, Rejected.
    Restricted to authenticated staff users.
    """
    job_filter_id = request.GET.get("job")
    jobs = JobPosting.objects.all().select_related("company")

    applications_qs = JobApplication.objects.select_related("job", "job__company", "candidate")
    if job_filter_id:
        try:
            applications_qs = applications_qs.filter(job_id=int(job_filter_id))
        except (ValueError, TypeError):
            pass

    # Pipeline stages
    applied_apps = applications_qs.filter(status=JobApplication.STATUS_APPLIED)
    review_apps = applications_qs.filter(status=JobApplication.STATUS_UNDER_REVIEW)
    shortlisted_apps = applications_qs.filter(status=JobApplication.STATUS_SHORTLISTED)
    rejected_apps = applications_qs.filter(status=JobApplication.STATUS_REJECTED)

    # Summary metrics
    metrics = {
        "total_jobs": jobs.count(),
        "active_jobs": jobs.filter(active=True).count(),
        "total_applications": applications_qs.count(),
        "applied_count": applied_apps.count(),
        "review_count": review_apps.count(),
        "shortlisted_count": shortlisted_apps.count(),
        "rejected_count": rejected_apps.count(),
    }

    context = {
        "jobs": jobs,
        "selected_job_id": int(job_filter_id) if job_filter_id and job_filter_id.isdigit() else None,
        "applications": applications_qs,
        "applied_apps": applied_apps,
        "review_apps": review_apps,
        "shortlisted_apps": shortlisted_apps,
        "rejected_apps": rejected_apps,
        "metrics": metrics,
        "status_choices": JobApplication.STATUS_CHOICES,
    }
    return render(request, "jobs/recruiter_dashboard.html", context)


@require_POST
@login_required(login_url="login")
@user_passes_test(is_recruiter, login_url="login")
def update_application_status(request, pk):
    """Update status of a candidate application in the hiring pipeline."""
    application = get_object_or_404(JobApplication, pk=pk)
    
    new_status = request.POST.get("status")
    if not new_status and request.content_type == "application/json":
        try:
            data = json.loads(request.body.decode("utf-8"))
            new_status = data.get("status")
        except json.JSONDecodeError:
            pass

    valid_statuses = [choice[0] for choice in JobApplication.STATUS_CHOICES]
    if new_status in valid_statuses:
        application.status = new_status
        application.save()
        
        is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest" or request.content_type == "application/json"
        if is_ajax:
            return JsonResponse({
                "success": True,
                "application_id": application.id,
                "new_status": application.status,
                "badge_class": application.status_badge_class,
                "message": f"Application status updated to '{application.status}'."
            })
        messages.success(request, f"Updated {application.candidate.full_name}'s status to {new_status}.")
    else:
        messages.error(request, "Invalid status choice.")

    return redirect("recruiter_dashboard")


@login_required(login_url="login")
@user_passes_test(is_recruiter, login_url="login")
def recruiter_job_create(request):
    """Create a new job posting from the recruiter portal."""
    if request.method == "POST":
        form = JobPostingForm(request.POST)
        if form.is_valid():
            job = form.save()
            messages.success(request, f"Job '{job.title}' created successfully!")
            return redirect("recruiter_dashboard")
    else:
        form = JobPostingForm()
    
    return render(request, "jobs/job_form.html", {
        "form": form,
        "title": "Post New Job",
        "action": "Create Job",
    })


@login_required(login_url="login")
@user_passes_test(is_recruiter, login_url="login")
def recruiter_job_edit(request, pk):
    """Edit an existing job posting."""
    job = get_object_or_404(JobPosting, pk=pk)
    if request.method == "POST":
        form = JobPostingForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, f"Job '{job.title}' updated successfully!")
            return redirect("recruiter_dashboard")
    else:
        form = JobPostingForm(instance=job)

    return render(request, "jobs/job_form.html", {
        "form": form,
        "title": f"Edit Job: {job.title}",
        "action": "Update Job",
        "job": job,
    })


@require_POST
@login_required(login_url="login")
@user_passes_test(is_recruiter, login_url="login")
def recruiter_job_toggle(request, pk):
    """Quickly toggle active/inactive status of a job posting."""
    job = get_object_or_404(JobPosting, pk=pk)
    job.active = not job.active
    job.save()
    status_text = "activated" if job.active else "deactivated"
    messages.info(request, f"Job '{job.title}' {status_text}.")
    return redirect("recruiter_dashboard")


def candidate_applications(request):
    """Candidate portal to check application status and profile details."""
    email_query = request.GET.get("email", "").strip().lower()
    candidate = None
    applications = []

    if email_query:
        candidate = Candidate.objects.filter(email__iexact=email_query).first()
        if candidate:
            applications = candidate.applications.select_related("job", "job__company").all()
        else:
            messages.info(request, f"No candidate record found for email: {email_query}")

    context = {
        "email_query": email_query,
        "candidate": candidate,
        "applications": applications,
    }
    return render(request, "jobs/candidate_portal.html", context)


def recruiter_login(request):
    """Recruiter / Staff login view with demo helper credentials."""
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("recruiter_dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_staff:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                next_url = request.GET.get("next") or request.POST.get("next") or "recruiter_dashboard"
                return redirect(next_url)
            else:
                messages.error(request, "Access restricted: User is not authorized as a staff recruiter.")
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "jobs/login.html")


def recruiter_logout(request):
    """Logout authenticated user."""
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect("job_list")


def api_jobs(request):
    """JSON API endpoint returning active jobs for JavaScript client-side processing."""
    jobs = JobPosting.objects.filter(active=True).select_related("company")
    data = []
    for job in jobs:
        data.append({
            "id": job.id,
            "title": job.title,
            "company": job.company.name,
            "company_logo": job.company.logo_url,
            "company_website": job.company.website,
            "location": job.company.location,
            "job_type": job.job_type,
            "salary_range": job.salary_range,
            "required_skills": job.skills_list(),
            "description": job.description[:200] + "..." if len(job.description) > 200 else job.description,
            "posted_date": job.posted_date.strftime("%b %d, %Y"),
        })
    return JsonResponse({"jobs": data})
