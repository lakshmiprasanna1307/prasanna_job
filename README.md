# JobPulse ATS & Job Board Platform

**Full-Stack Recruitment Portal & Applicant Tracking System (ATS)**  
*Django 6.x • SQLite • Bootstrap 5.3 • WhiteNoise • Gunicorn • Render Ready*

---

## 🌟 Overview & Key Features

JobPulse ATS is a recruitment platform connecting candidates and hiring teams:
- **Active Job Board (`/`)**: Responsive Bootstrap 5 job cards featuring company details, locations, compensation ranges, job types, and skill tags.
- **Instant Client-Side Filtering**: Real-time keyword search, work arrangement dropdown, location filter, and interactive skill pills that filter jobs instantly without page reload.
- **Application Workflow & Modal (`/jobs/<id>/` & modal)**: Bootstrap application modal with client-side field validation, asynchronous AJAX submission, and duplicate prevention.
- **Recruiter ATS Pipeline Dashboard (`/recruiter/dashboard/`)**:
  - Four recruitment stages: **Applied**, **Under Review**, **Shortlisted**, and **Rejected**.
  - Interactive Kanban board and searchable table view.
  - Pipeline metrics summary cards (Active jobs, total applicants, stage counts).
  - Quick stage transitions (moves applicants between columns with instant status update).
  - Candidate profile and cover letter modal preview.
- **Candidate Portal (`/portal/`)**: Allows candidates to check their application status, view review timeline, and see their profile data.
- **Staff-Only Access Control**: Recruiter dashboard and actions are restricted to authenticated staff users.
- **Business Logic Protection**: Prevents duplicate applications for the same position by email, validates phone/email/skills, and protects forms with CSRF tokens.

---

## 🔑 Demo Recruiter Credentials

| Role | Username | Password | Email |
| :--- | :--- | :--- | :--- |
| **Recruiter (Staff)** | `recruiter` | `recruiter123` | `recruiter@atsportal.com` |

---

## 🛠️ Technology Stack

- **Backend**: Python 3.12+, Django 6.1+, Django ORM
- **Database**: SQLite (`db.sqlite3`) as required
- **Frontend**: HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3, Bootstrap Icons
- **Production Server**: Gunicorn 26.x, WhiteNoise 6.x
- **Hosting Target**: Render Web Service / Blueprint

---

## 🚀 Local Development Setup

1. **Activate Virtual Environment**:
   ```powershell
   # Windows
   .\venv\Scripts\activate
   # macOS / Linux
   source venv/bin/activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Apply Database Migrations**:
   ```bash
   python manage.py migrate
   ```

4. **Seed Sample Data & Create Superuser**:
   ```bash
   python manage.py seed_data
   python create_superuser.py
   ```

5. **Run Development Server**:
   ```bash
   python manage.py runserver
   ```
   Open `http://127.0.0.1:8000/` in your browser.

---

## 🧪 Running Automated Tests

Run the full Django test suite covering models, forms, validation, duplicate prevention, and recruiter access controls:
```bash
python manage.py test jobs
```

---

## ☁️ Render Deployment Instructions

1. **Push Repository to GitHub**:
   ```bash
   git add .
   git commit -m "Deploy JobPulse ATS on Render"
   git push origin main
   ```

2. **Deploy on Render**:
   - Go to [dashboard.render.com](https://dashboard.render.com).
   - Select **New +** → **Blueprint** (or **Web Service**).
   - Connect your GitHub repository.
   - If using **Web Service** manually:
     - **Runtime**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --no-input && python manage.py migrate && python create_superuser.py`
     - **Start Command**: `python manage.py migrate && python create_superuser.py && gunicorn prasanna_job.wsgi:application`
     - **Environment Variables**:
       - `RENDER`: `True`
       - `SECRET_KEY`: `<your-secure-random-secret-key>`
       - `PYTHON_VERSION`: `3.11.0` (or `3.12.0`)
3. **Open Live URL**:
   Your application will be live at `https://<service-name>.onrender.com`. Sign in to `/login/` with `recruiter` / `recruiter123`.
