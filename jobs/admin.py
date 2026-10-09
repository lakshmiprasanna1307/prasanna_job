from django.contrib import admin
from .models import Company, JobPosting, Candidate, JobApplication


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "location", "website", "created_at")
    search_fields = ("name", "location")
    list_filter = ("location",)


class JobApplicationInline(admin.TabularInline):
    model = JobApplication
    extra = 0
    readonly_fields = ("applied_date",)
    fields = ("candidate", "status", "applied_date")


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "job_type", "salary_range", "active", "posted_date", "total_applications")
    list_filter = ("job_type", "active", "company")
    search_fields = ("title", "company__name", "required_skills", "description")
    list_editable = ("active",)
    inlines = [JobApplicationInline]


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "phone", "skills", "created_at")
    search_fields = ("full_name", "email", "skills")
    list_filter = ("created_at",)


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ("candidate", "job", "status", "applied_date")
    list_filter = ("status", "applied_date", "job__job_type")
    search_fields = ("candidate__full_name", "candidate__email", "job__title", "job__company__name")
    list_editable = ("status",)
