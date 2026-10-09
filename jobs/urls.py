from django.urls import path
from . import views

urlpatterns = [
    path("", views.job_list, name="job_list"),
    path("jobs/<int:pk>/", views.job_detail, name="job_detail"),
    path("jobs/apply/", views.apply_job, name="apply_job"),
    path("recruiter/dashboard/", views.recruiter_dashboard, name="recruiter_dashboard"),
    path("recruiter/applications/<int:pk>/status/", views.update_application_status, name="update_application_status"),
    path("recruiter/jobs/new/", views.recruiter_job_create, name="recruiter_job_create"),
    path("recruiter/jobs/<int:pk>/edit/", views.recruiter_job_edit, name="recruiter_job_edit"),
    path("recruiter/jobs/<int:pk>/toggle/", views.recruiter_job_toggle, name="recruiter_job_toggle"),
    path("portal/", views.candidate_applications, name="candidate_portal"),
    path("login/", views.recruiter_login, name="login"),
    path("logout/", views.recruiter_logout, name="logout"),
    path("api/jobs/", views.api_jobs, name="api_jobs"),
]
