from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from jobs.models import Company, JobPosting, Candidate, JobApplication
from jobs.forms import JobApplicationForm

User = get_user_model()


class RecruitmentPortalTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Create test company
        self.company = Company.objects.create(
            name="Acme Corp",
            website="https://acme.example.com",
            location="San Francisco, CA",
            logo_url="https://acme.example.com/logo.png"
        )

        # Create test job
        self.job = JobPosting.objects.create(
            company=self.company,
            title="Senior Python Engineer",
            job_type="Full-time",
            required_skills="Python, Django, PostgreSQL",
            salary_range="$120k - $150k",
            description="We need a senior engineer.",
            active=True
        )

        # Create staff recruiter user
        self.recruiter = User.objects.create_user(
            username="recruiter_test",
            email="recruiter@example.com",
            password="password123",
            is_staff=True
        )

        # Create standard non-staff user
        self.standard_user = User.objects.create_user(
            username="regular_user",
            email="regular@example.com",
            password="password123",
            is_staff=False
        )

    def test_job_listing_view(self):
        """Active jobs appear in job listing."""
        response = self.client.get(reverse("job_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Senior Python Engineer")
        self.assertContains(response, "Acme Corp")

    def test_job_detail_view(self):
        """Job detail page displays company, requirements, and salary."""
        response = self.client.get(reverse("job_detail", kwargs={"pk": self.job.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.job.title)
        self.assertContains(response, "$120k - $150k")

    def test_application_submission_and_duplicate_prevention(self):
        """Candidate can apply once, and duplicate application to same job is rejected."""
        payload = {
            "job_id": self.job.pk,
            "full_name": "Test Candidate",
            "email": "candidate@example.com",
            "phone": "+1 555 123 4567",
            "portfolio_url": "https://example.com/portfolio",
            "skills": "Python, Django",
            "cover_letter": "I would love to work at Acme Corp as a Python developer."
        }

        # 1. First submission should succeed
        response = self.client.post(reverse("apply_job"), payload, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(JobApplication.objects.filter(job=self.job).count(), 1)

        # 2. Second submission with SAME email and job MUST fail due to duplicate prevention
        response_dup = self.client.post(reverse("apply_job"), payload, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(response_dup.status_code, 400)
        data_dup = response_dup.json()
        self.assertFalse(data_dup["success"])
        self.assertIn("already submitted an application", data_dup["error"].lower())

    def test_candidate_validation_invalid_phone(self):
        """Form rejects invalid phone numbers."""
        form = JobApplicationForm(data={
            "job_id": self.job.pk,
            "full_name": "John Doe",
            "email": "johndoe@example.com",
            "phone": "123", # Too short
            "skills": "Python",
            "cover_letter": "A full cover letter for testing invalid phone.",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("phone", form.errors)

    def test_recruiter_dashboard_access_control(self):
        """Recruiter dashboard is staff-only."""
        # Unauthenticated user should be redirected to login
        response = self.client.get(reverse("recruiter_dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

        # Standard non-staff user should be redirected to login
        self.client.login(username="regular_user", password="password123")
        response = self.client.get(reverse("recruiter_dashboard"))
        self.assertEqual(response.status_code, 302)
        self.client.logout()

        # Staff recruiter should have access
        self.client.login(username="recruiter_test", password="password123")
        response = self.client.get(reverse("recruiter_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Applicant Tracking System (ATS) Pipeline")

    def test_update_application_status(self):
        """Recruiter can move candidate through pipeline stages."""
        candidate = Candidate.objects.create(
            full_name="Bob Smith",
            email="bob@example.com",
            phone="+1 555 987 6543",
            skills="Django"
        )
        app = JobApplication.objects.create(
            job=self.job,
            candidate=candidate,
            cover_letter="Bob's letter",
            status=JobApplication.STATUS_APPLIED
        )

        self.client.login(username="recruiter_test", password="password123")
        
        # Move to Under Review
        response = self.client.post(
            reverse("update_application_status", kwargs={"pk": app.pk}),
            {"status": JobApplication.STATUS_UNDER_REVIEW}
        )
        self.assertEqual(response.status_code, 302)
        app.refresh_from_db()
        self.assertEqual(app.status, JobApplication.STATUS_UNDER_REVIEW)

        # Move to Shortlisted
        self.client.post(
            reverse("update_application_status", kwargs={"pk": app.pk}),
            {"status": JobApplication.STATUS_SHORTLISTED}
        )
        app.refresh_from_db()
        self.assertEqual(app.status, JobApplication.STATUS_SHORTLISTED)

    def test_api_jobs_endpoint(self):
        """API jobs returns JSON with active job details."""
        response = self.client.get(reverse("api_jobs"))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("jobs", data)
        self.assertEqual(len(data["jobs"]), 1)
        self.assertEqual(data["jobs"][0]["title"], "Senior Python Engineer")
