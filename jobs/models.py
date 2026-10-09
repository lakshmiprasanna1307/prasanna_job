from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=200)
    website = models.URLField(max_length=300, blank=True)
    location = models.CharField(max_length=150)
    logo_url = models.URLField(max_length=500, blank=True, help_text="Direct URL to company logo")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Companies"
        ordering = ["name"]

    def __str__(self):
        return self.name


class JobPosting(models.Model):
    JOB_TYPE_CHOICES = [
        ("Full-time", "Full-time"),
        ("Part-time", "Part-time"),
        ("Remote", "Remote"),
        ("Contract", "Contract"),
        ("Internship", "Internship"),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="job_postings")
    title = models.CharField(max_length=250)
    job_type = models.CharField(max_length=50, choices=JOB_TYPE_CHOICES, default="Full-time")
    required_skills = models.CharField(
        max_length=300, 
        help_text="Comma-separated skills (e.g. Python, Django, PostgreSQL, Docker)"
    )
    salary_range = models.CharField(max_length=100, help_text="e.g. $90,000 - $120,000 / year")
    description = models.TextField()
    active = models.BooleanField(default=True, verbose_name="Active Flag")
    posted_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-posted_date"]

    def __str__(self):
        return f"{self.title} at {self.company.name}"

    def skills_list(self):
        """Returns required skills as a clean list."""
        if not self.required_skills:
            return []
        return [skill.strip() for skill in self.required_skills.split(",") if skill.strip()]

    @property
    def total_applications(self):
        return self.applications.count()


class Candidate(models.Model):
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    portfolio_url = models.URLField(max_length=300, blank=True)
    skills = models.CharField(
        max_length=300, 
        help_text="Comma-separated skills (e.g. Python, React, UI/UX)"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} ({self.email})"

    def skills_list(self):
        """Returns candidate skills as a clean list."""
        if not self.skills:
            return []
        return [skill.strip() for skill in self.skills.split(",") if skill.strip()]


class JobApplication(models.Model):
    STATUS_APPLIED = "Applied"
    STATUS_UNDER_REVIEW = "Under Review"
    STATUS_SHORTLISTED = "Shortlisted"
    STATUS_REJECTED = "Rejected"

    STATUS_CHOICES = [
        (STATUS_APPLIED, "Applied"),
        (STATUS_UNDER_REVIEW, "Under Review"),
        (STATUS_SHORTLISTED, "Shortlisted"),
        (STATUS_REJECTED, "Rejected"),
    ]

    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name="applications")
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name="applications")
    cover_letter = models.TextField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=STATUS_APPLIED)
    applied_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-applied_date"]
        constraints = [
            models.UniqueConstraint(
                fields=["job", "candidate"],
                name="unique_candidate_job_application",
            )
        ]

    def __str__(self):
        return f"{self.candidate.full_name} -> {self.job.title} ({self.status})"

    @property
    def status_badge_class(self):
        mapping = {
            self.STATUS_APPLIED: "bg-primary",
            self.STATUS_UNDER_REVIEW: "bg-warning text-dark",
            self.STATUS_SHORTLISTED: "bg-success",
            self.STATUS_REJECTED: "bg-danger",
        }
        return mapping.get(self.status, "bg-secondary")
