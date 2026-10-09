import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "prasanna_job.settings")
django.setup()

from django.contrib.auth import get_user_model
from django.core.management import call_command
from jobs.models import Company

User = get_user_model()

username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "recruiter")
email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "recruiter@atsportal.com")
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "recruiter123")

if not User.objects.filter(username=username).exists():
    print(f"Creating superuser '{username}'...")
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Superuser '{username}' created successfully!")
else:
    print(f"Superuser '{username}' already exists.")

# Auto-seed sample jobs if database is empty (ideal for fresh Render deploys)
if Company.objects.count() == 0:
    try:
        print("Empty database detected. Seeding sample data...")
        call_command("seed_data")
    except Exception as e:
        print(f"Error auto-seeding sample data: {e}")
