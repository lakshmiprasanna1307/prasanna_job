from django.core.management.base import BaseCommand
from jobs.models import Company, JobPosting, Candidate, JobApplication


class Command(BaseCommand):
    help = "Seed database with realistic initial companies, jobs, candidates, and applications"

    def handle(self, *args, **options):
        self.stdout.write("Seeding database with realistic sample data...")

        # 1. Companies
        companies_data = [
            {
                "name": "Stripe",
                "website": "https://stripe.com",
                "location": "San Francisco, CA",
                "logo_url": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=128&auto=format&fit=crop&q=80",
            },
            {
                "name": "Spotify",
                "website": "https://spotify.com",
                "location": "New York, NY (Remote)",
                "logo_url": "https://images.unsplash.com/photo-1614680376593-902f749f7ffc?w=128&auto=format&fit=crop&q=80",
            },
            {
                "name": "Vercel",
                "website": "https://vercel.com",
                "location": "Remote",
                "logo_url": "https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=128&auto=format&fit=crop&q=80",
            },
            {
                "name": "GitHub",
                "website": "https://github.com",
                "location": "San Francisco, CA",
                "logo_url": "https://images.unsplash.com/photo-1618401471353-b98aedd04e11?w=128&auto=format&fit=crop&q=80",
            },
            {
                "name": "Airbnb",
                "website": "https://airbnb.com",
                "location": "Seattle, WA",
                "logo_url": "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=128&auto=format&fit=crop&q=80",
            },
            {
                "name": "TechNova Labs",
                "website": "https://technova.io",
                "location": "Austin, TX",
                "logo_url": "https://images.unsplash.com/photo-1507238691740-187a5b1d37b8?w=128&auto=format&fit=crop&q=80",
            },
        ]

        companies = {}
        for c_data in companies_data:
            comp, created = Company.objects.get_or_create(
                name=c_data["name"],
                defaults=c_data
            )
            companies[comp.name] = comp
            status = "Created" if created else "Found"
            self.stdout.write(f"[{status}] Company: {comp.name}")

        # 2. Job Postings
        jobs_data = [
            {
                "company": companies["Stripe"],
                "title": "Senior Full Stack Engineer (Python & React)",
                "job_type": "Full-time",
                "required_skills": "Python, Django, React, TypeScript, PostgreSQL, Docker",
                "salary_range": "$135,000 - $170,000 / year",
                "description": "We are seeking a seasoned Senior Full Stack Engineer to build high-availability financial tools, billing portals, and API gateways. You will collaborate with product designers, implement resilient data pipelines, and architect secure transactional backends.",
                "active": True,
            },
            {
                "company": companies["Spotify"],
                "title": "Lead Django Backend Architect",
                "job_type": "Remote",
                "required_skills": "Python, Django, Celery, Redis, Kubernetes, AWS",
                "salary_range": "$145,000 - $185,000 / year",
                "description": "Join our Core Platform squad to scale streaming recommendation engines and user analytics. You will spearhead async processing using Celery and Redis, build RESTful microservices, and ensure sub-100ms response times globally.",
                "active": True,
            },
            {
                "company": companies["Vercel"],
                "title": "Cloud DevOps & Platform SRE",
                "job_type": "Remote",
                "required_skills": "Docker, Kubernetes, Terraform, CI/CD, Linux, Python",
                "salary_range": "$130,000 - $160,000 / year",
                "description": "Ensure five-nines uptime for global edge networks. You will automate deployment pipelines, implement observability with Prometheus and Datadog, and maintain multi-region infrastructure as code.",
                "active": True,
            },
            {
                "company": companies["GitHub"],
                "title": "Frontend UI/UX Engineer",
                "job_type": "Full-time",
                "required_skills": "JavaScript, HTML5, CSS3, Bootstrap 5, Accessibility, Webpack",
                "salary_range": "$115,000 - $145,000 / year",
                "description": "Craft intuitive developer workflows, sleek dashboard components, and WCAG-compliant design systems. Experience with responsive layouts, CSS custom properties, and modern JavaScript is essential.",
                "active": True,
            },
            {
                "company": companies["TechNova Labs"],
                "title": "AI & Data Pipeline Engineer",
                "job_type": "Full-time",
                "required_skills": "Python, Django, Pandas, PyTorch, SQL, Airflow",
                "salary_range": "$125,000 - $155,000 / year",
                "description": "Build high-throughput ingestion pipelines for large language model inference and predictive analytics. You will interface with data scientists and deploy production-grade data APIs.",
                "active": True,
            },
            {
                "company": companies["Airbnb"],
                "title": "Product Growth Manager",
                "job_type": "Full-time",
                "required_skills": "Product Strategy, A/B Testing, SQL, Agile, Analytics",
                "salary_range": "$120,000 - $150,000 / year",
                "description": "Drive user acquisition, candidate matching algorithms, and conversion funnels across our marketplace. Lead cross-functional sprint teams of engineers and product designers.",
                "active": True,
            },
            {
                "company": companies["Stripe"],
                "title": "Junior Python Developer",
                "job_type": "Internship",
                "required_skills": "Python, Django, Git, SQLite, REST APIs",
                "salary_range": "$65,000 - $80,000 / year",
                "description": "An exceptional learning and growth opportunity for upcoming graduates or self-taught developers. You will pair with Senior Engineers, write unit tests, and implement internal developer tooling.",
                "active": True,
            },
            {
                "company": companies["Spotify"],
                "title": "Mobile Systems Engineer",
                "job_type": "Contract",
                "required_skills": "React Native, TypeScript, iOS, Android, REST APIs",
                "salary_range": "$95,000 - $125,000 / year",
                "description": "Build responsive audio playback widgets, offline synchronization, and dynamic playlists for millions of mobile devices.",
                "active": True,
            },
            {
                "company": companies["GitHub"],
                "title": "Cybersecurity & Identity Analyst",
                "job_type": "Remote",
                "required_skills": "OAuth, SAML, Python, Penetration Testing, IAM",
                "salary_range": "$120,000 - $150,000 / year",
                "description": "Protect critical developer infrastructure and token authentication gateways. Implement security scanning in CI/CD pipelines and lead audit reviews.",
                "active": True,
            },
        ]

        jobs = []
        for j_data in jobs_data:
            job, created = JobPosting.objects.get_or_create(
                title=j_data["title"],
                company=j_data["company"],
                defaults=j_data
            )
            jobs.append(job)
            status = "Created" if created else "Found"
            self.stdout.write(f"[{status}] JobPosting: {job.title}")

        # 3. Candidates
        candidates_data = [
            {
                "full_name": "Alexander Wright",
                "email": "alex.wright@example.com",
                "phone": "+1 415 555 0142",
                "portfolio_url": "https://github.com/alexwright-dev",
                "skills": "Python, Django, React, PostgreSQL, Docker, Redis",
            },
            {
                "full_name": "Samantha Chen",
                "email": "samantha.chen@example.com",
                "phone": "+1 206 555 0188",
                "portfolio_url": "https://samanthachen.design",
                "skills": "JavaScript, HTML5, CSS3, Bootstrap 5, Figma, UI/UX",
            },
            {
                "full_name": "Marcus Vance",
                "email": "marcus.vance@example.com",
                "phone": "+1 512 555 0199",
                "portfolio_url": "https://github.com/marcusvance-sre",
                "skills": "Kubernetes, Docker, Terraform, Linux, CI/CD, Python",
            },
            {
                "full_name": "Elena Rostova",
                "email": "elena.rostova@example.com",
                "phone": "+1 646 555 0173",
                "portfolio_url": "https://github.com/erostova-ai",
                "skills": "Python, PyTorch, Pandas, SQL, Django, Airflow",
            },
            {
                "full_name": "David Kim",
                "email": "david.kim@example.com",
                "phone": "+1 408 555 0165",
                "portfolio_url": "https://davidkim.dev",
                "skills": "Python, Django, SQLite, REST APIs, Git",
            },
            {
                "full_name": "Priya Sharma",
                "email": "priya.sharma@example.com",
                "phone": "+1 312 555 0134",
                "portfolio_url": "https://github.com/priyasharma-web",
                "skills": "React Native, TypeScript, iOS, Android, REST APIs",
            },
            {
                "full_name": "Lucas Morales",
                "email": "lucas.morales@example.com",
                "phone": "+1 617 555 0122",
                "portfolio_url": "https://lucasmorales.tech",
                "skills": "OAuth, SAML, Python, IAM, Linux, Security Audits",
            },
            {
                "full_name": "Chloe Bennett",
                "email": "chloe.bennett@example.com",
                "phone": "+1 415 555 0110",
                "portfolio_url": "https://chloebennett.pm",
                "skills": "Product Strategy, A/B Testing, SQL, Agile, Analytics",
            },
        ]

        candidates = {}
        for c_data in candidates_data:
            cand, created = Candidate.objects.get_or_create(
                email=c_data["email"],
                defaults=c_data
            )
            candidates[cand.email] = cand
            status = "Created" if created else "Found"
            self.stdout.write(f"[{status}] Candidate: {cand.full_name}")

        # 4. Job Applications across all 4 pipeline stages
        applications_data = [
            {
                "job": jobs[0],
                "candidate": candidates["alex.wright@example.com"],
                "cover_letter": "I have spent the last 5 years scaling payment flow web applications with Python/Django and React. My past achievements include reducing API latency by 35% and designing reliable webhook consumers. I would love to bring this expertise to Stripe.",
                "status": JobApplication.STATUS_SHORTLISTED,
            },
            {
                "job": jobs[1],
                "candidate": candidates["alex.wright@example.com"],
                "cover_letter": "I am deeply passionate about distributed systems and audio media. Having architected complex async pipelines with Celery and Redis, I am eager to contribute to Spotify's recommendation core.",
                "status": JobApplication.STATUS_UNDER_REVIEW,
            },
            {
                "job": jobs[3],
                "candidate": candidates["samantha.chen@example.com"],
                "cover_letter": "I specialize in clean, accessible design systems and semantic HTML5/Bootstrap layouts. Building tools that millions of developers rely on every day at GitHub is my ultimate dream.",
                "status": JobApplication.STATUS_SHORTLISTED,
            },
            {
                "job": jobs[2],
                "candidate": candidates["marcus.vance@example.com"],
                "cover_letter": "With 6 years of infrastructure automation using Terraform, Kubernetes, and GitHub Actions, I have maintained 99.99% uptime across production clusters.",
                "status": JobApplication.STATUS_UNDER_REVIEW,
            },
            {
                "job": jobs[4],
                "candidate": candidates["elena.rostova@example.com"],
                "cover_letter": "My research and production background in building scalable PyTorch feature extractors and Airflow DAGs directly matches TechNova's engineering vision.",
                "status": JobApplication.STATUS_APPLIED,
            },
            {
                "job": jobs[6],
                "candidate": candidates["david.kim@example.com"],
                "cover_letter": "As an enthusiastic junior developer with hands-on coursework in Django and relational databases, I am eager to absorb best practices from Stripe's engineering mentors.",
                "status": JobApplication.STATUS_APPLIED,
            },
            {
                "job": jobs[7],
                "candidate": candidates["priya.sharma@example.com"],
                "cover_letter": "I have published multiple cross-platform React Native applications with smooth 60fps animations, background audio playback, and SQLite caching.",
                "status": JobApplication.STATUS_UNDER_REVIEW,
            },
            {
                "job": jobs[8],
                "candidate": candidates["lucas.morales@example.com"],
                "cover_letter": "Having performed comprehensive penetration audits and automated security policy compliance, I am excited to support GitHub's IAM architecture.",
                "status": JobApplication.STATUS_SHORTLISTED,
            },
            {
                "job": jobs[5],
                "candidate": candidates["chloe.bennett@example.com"],
                "cover_letter": "I have successfully launched two core marketplace growth experiments yielding a 22% increase in host retention and lead conversion.",
                "status": JobApplication.STATUS_APPLIED,
            },
            {
                "job": jobs[0],
                "candidate": candidates["david.kim@example.com"],
                "cover_letter": "Applying for Senior Full Stack role to challenge myself and gain exposure to high-scale financial technology.",
                "status": JobApplication.STATUS_REJECTED,
            },
            {
                "job": jobs[2],
                "candidate": candidates["samantha.chen@example.com"],
                "cover_letter": "Interested in cloud infrastructure and edge networking systems.",
                "status": JobApplication.STATUS_REJECTED,
            },
            {
                "job": jobs[3],
                "candidate": candidates["lucas.morales@example.com"],
                "cover_letter": "Transitioning towards web interfaces and dashboard frontend design.",
                "status": JobApplication.STATUS_UNDER_REVIEW,
            },
        ]

        for app_data in applications_data:
            app, created = JobApplication.objects.get_or_create(
                job=app_data["job"],
                candidate=app_data["candidate"],
                defaults={
                    "cover_letter": app_data["cover_letter"],
                    "status": app_data["status"],
                }
            )
            status = "Created" if created else "Found"
            self.stdout.write(f"[{status}] Application: {app.candidate.full_name} -> {app.job.title} ({app.status})")

        self.stdout.write(self.style.SUCCESS("Database seeding completed successfully!"))
