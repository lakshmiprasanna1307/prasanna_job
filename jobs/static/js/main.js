/**
 * JobPulse ATS & Job Portal - Main Interactive JavaScript
 * Implements:
 * 1. Live keyword & skill filtering without page reload
 * 2. Bootstrap application modal with client-side validation & AJAX submission
 * 3. Recruiter ATS pipeline quick status updates & candidate detail preview
 */

document.addEventListener("DOMContentLoaded", function () {
  initLiveJobFilter();
  initApplicationModal();
  initRecruiterDashboard();
});

/* ==========================================================================
   1. Live Job Keyword, Skill, Type & Location Filtering (No Reload)
   ========================================================================== */
function initLiveJobFilter() {
  const searchInput = document.getElementById("jobSearchInput");
  const jobTypeFilter = document.getElementById("jobTypeFilter");
  const locationFilter = document.getElementById("locationFilter");
  const skillPills = document.querySelectorAll(".filter-pill[data-skill]");
  const clearFiltersBtn = document.getElementById("clearFiltersBtn");
  const jobCards = document.querySelectorAll(".job-card-item");
  const jobsCountBadge = document.getElementById("visibleJobsCount");
  const noResultsAlert = document.getElementById("noJobsFoundAlert");

  if (!jobCards.length) return;

  let activeSkills = new Set();

  function applyFilters() {
    const keyword = (searchInput ? searchInput.value : "").toLowerCase().trim();
    const selectedType = (jobTypeFilter ? jobTypeFilter.value : "all").toLowerCase();
    const selectedLocation = (locationFilter ? locationFilter.value : "all").toLowerCase();

    let visibleCount = 0;

    jobCards.forEach((card) => {
      const title = card.getAttribute("data-title") || "";
      const company = card.getAttribute("data-company") || "";
      const description = card.getAttribute("data-description") || "";
      const jobType = (card.getAttribute("data-type") || "").toLowerCase();
      const location = (card.getAttribute("data-location") || "").toLowerCase();
      const cardSkills = (card.getAttribute("data-skills") || "").toLowerCase().split(",");

      // 1. Keyword check
      const matchesKeyword =
        !keyword ||
        title.includes(keyword) ||
        company.includes(keyword) ||
        description.includes(keyword) ||
        cardSkills.some(s => s.trim().includes(keyword));

      // 2. Job type check
      const matchesType = (selectedType === "all" || !selectedType) || jobType === selectedType;

      // 3. Location check
      const matchesLocation = (selectedLocation === "all" || !selectedLocation) || location.includes(selectedLocation);

      // 4. Skills check (must match all selected skills if any active)
      let matchesSkills = true;
      if (activeSkills.size > 0) {
        for (let skill of activeSkills) {
          const sLower = skill.toLowerCase();
          const hasSkill = cardSkills.some(cs => cs.trim() === sLower || cs.trim().includes(sLower));
          if (!hasSkill) {
            matchesSkills = false;
            break;
          }
        }
      }

      if (matchesKeyword && matchesType && matchesLocation && matchesSkills) {
        card.style.display = "";
        card.classList.add("animate-fade-in");
        visibleCount++;
      } else {
        card.style.display = "none";
        card.classList.remove("animate-fade-in");
      }
    });

    // Update count badge
    if (jobsCountBadge) {
      jobsCountBadge.textContent = visibleCount;
    }

    // Toggle empty state alert
    if (noResultsAlert) {
      if (visibleCount === 0) {
        noResultsAlert.classList.remove("d-none");
      } else {
        noResultsAlert.classList.add("d-none");
      }
    }
  }

  // Event Listeners for Filters
  if (searchInput) {
    searchInput.addEventListener("input", applyFilters);
  }

  if (jobTypeFilter) {
    jobTypeFilter.addEventListener("change", applyFilters);
  }

  if (locationFilter) {
    locationFilter.addEventListener("change", applyFilters);
  }

  skillPills.forEach((pill) => {
    pill.addEventListener("click", function () {
      const skillName = this.getAttribute("data-skill");
      if (activeSkills.has(skillName)) {
        activeSkills.delete(skillName);
        this.classList.remove("active");
      } else {
        activeSkills.add(skillName);
        this.classList.add("active");
      }
      applyFilters();
    });
  });

  if (clearFiltersBtn) {
    clearFiltersBtn.addEventListener("click", function (e) {
      e.preventDefault();
      if (searchInput) searchInput.value = "";
      if (jobTypeFilter) jobTypeFilter.value = "all";
      if (locationFilter) locationFilter.value = "all";
      activeSkills.clear();
      skillPills.forEach(p => p.classList.remove("active"));
      applyFilters();
    });
  }

  // Initial call
  applyFilters();
}

/* ==========================================================================
   2. Bootstrap Application Modal & Client-Side Validation
   ========================================================================== */
function initApplicationModal() {
  const modalEl = document.getElementById("applicationModal");
  if (!modalEl) return;

  const appForm = document.getElementById("jobApplicationForm");
  const jobTitleSpan = document.getElementById("modalJobTitle");
  const companySpan = document.getElementById("modalJobCompany");
  const hiddenJobId = document.getElementById("app_job_id");
  const alertContainer = document.getElementById("modalAlertContainer");
  const submitBtn = document.getElementById("submitApplicationBtn");

  // Open modal triggers
  document.querySelectorAll(".btn-open-apply-modal").forEach((btn) => {
    btn.addEventListener("click", function () {
      const jobId = this.getAttribute("data-job-id");
      const jobTitle = this.getAttribute("data-job-title");
      const companyName = this.getAttribute("data-company-name");

      if (hiddenJobId) hiddenJobId.value = jobId;
      if (jobTitleSpan) jobTitleSpan.textContent = jobTitle || "Position";
      if (companySpan) companySpan.textContent = companyName ? `at ${companyName}` : "";

      // Clear alert and previous validation states
      if (alertContainer) alertContainer.innerHTML = "";
      if (appForm) {
        appForm.classList.remove("was-validated");
        const errElems = appForm.querySelectorAll(".is-invalid");
        errElems.forEach(el => el.classList.remove("is-invalid"));
      }

      const modalInstance = bootstrap.Modal.getOrCreateInstance(modalEl);
      modalInstance.show();
    });
  });

  if (!appForm) return;

  // Client-side Validation and AJAX Submission
  appForm.addEventListener("submit", function (e) {
    e.preventDefault();

    const fullNameInput = document.getElementById("app_full_name");
    const emailInput = document.getElementById("app_email");
    const phoneInput = document.getElementById("app_phone");
    const portfolioInput = document.getElementById("app_portfolio_url");
    const skillsInput = document.getElementById("app_skills");
    const coverLetterInput = document.getElementById("app_cover_letter");

    let isValid = true;
    let errorMessages = [];

    // Reset classes
    [fullNameInput, emailInput, phoneInput, portfolioInput, skillsInput, coverLetterInput].forEach(inp => {
      if (inp) inp.classList.remove("is-invalid");
    });

    // Validate Full Name
    if (!fullNameInput.value.trim() || fullNameInput.value.trim().length < 2) {
      isValid = false;
      fullNameInput.classList.add("is-invalid");
      errorMessages.push("Please provide your full legal name (at least 2 characters).");
    }

    // Validate Email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(emailInput.value.trim())) {
      isValid = false;
      emailInput.classList.add("is-invalid");
      errorMessages.push("Please provide a valid email address.");
    }

    // Validate Phone (digits count between 7 and 15)
    const phoneDigits = phoneInput.value.replace(/\D/g, "");
    if (phoneDigits.length < 7 || phoneDigits.length > 15) {
      isValid = false;
      phoneInput.classList.add("is-invalid");
      errorMessages.push("Please enter a valid phone number with 7-15 digits.");
    }

    // Validate Skills
    if (!skillsInput.value.trim()) {
      isValid = false;
      skillsInput.classList.add("is-invalid");
      errorMessages.push("Please enter your relevant skills.");
    }

    // Validate Cover Letter
    if (!coverLetterInput.value.trim() || coverLetterInput.value.trim().length < 15) {
      isValid = false;
      coverLetterInput.classList.add("is-invalid");
      errorMessages.push("Please provide a cover letter introducing yourself (at least 15 characters).");
    }

    // Validate Portfolio URL if present
    if (portfolioInput && portfolioInput.value.trim()) {
      try {
        new URL(portfolioInput.value.trim());
      } catch (_) {
        isValid = false;
        portfolioInput.classList.add("is-invalid");
        errorMessages.push("Portfolio URL must be a valid web link starting with http:// or https://");
      }
    }

    if (!isValid) {
      if (alertContainer) {
        alertContainer.innerHTML = `
          <div class="alert alert-danger alert-dismissible fade show d-flex align-items-center" role="alert">
            <i class="bi bi-exclamation-triangle-fill me-2 fs-5"></i>
            <div>
              <strong>Validation Error:</strong><br>
              ${errorMessages.join("<br>")}
            </div>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
          </div>
        `;
      }
      return;
    }

    // Submit via AJAX
    const formData = new FormData(appForm);
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || "";

    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-2" role="status"></span>Submitting...`;
    }

    fetch(appForm.getAttribute("action") || "/jobs/apply/", {
      method: "POST",
      body: formData,
      headers: {
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRFToken": csrfToken
      }
    })
      .then(async (response) => {
        const data = await response.json();
        if (response.ok && data.success) {
          // Success Feedback
          if (alertContainer) {
            alertContainer.innerHTML = `
              <div class="alert alert-success d-flex align-items-center p-3" role="alert">
                <i class="bi bi-check-circle-fill me-2 fs-4"></i>
                <div>
                  <h6 class="alert-heading mb-1 fw-bold">Application Received!</h6>
                  <p class="mb-0 small">${data.message}</p>
                </div>
              </div>
            `;
          }
          appForm.reset();
          if (submitBtn) {
            submitBtn.style.display = "none";
          }
          setTimeout(() => {
            const modalInstance = bootstrap.Modal.getInstance(modalEl);
            if (modalInstance) modalInstance.hide();
            // Reload or toast
            window.location.reload();
          }, 2200);
        } else {
          // Server validation or duplicate error
          const errMsg = data.error || "Unable to submit application. Please review your details.";
          if (alertContainer) {
            alertContainer.innerHTML = `
              <div class="alert alert-danger d-flex align-items-center p-3" role="alert">
                <i class="bi bi-exclamation-octagon-fill me-2 fs-4"></i>
                <div>
                  <h6 class="alert-heading mb-1 fw-bold">Submission Failed</h6>
                  <p class="mb-0 small">${errMsg}</p>
                </div>
              </div>
            `;
          }
          if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = `Submit Application <i class="bi bi-send-fill ms-1"></i>`;
          }
        }
      })
      .catch((err) => {
        console.error("Submission error:", err);
        if (alertContainer) {
          alertContainer.innerHTML = `
            <div class="alert alert-danger d-flex align-items-center p-3" role="alert">
              <i class="bi bi-wifi-off me-2 fs-4"></i>
              <div>
                <h6 class="alert-heading mb-1 fw-bold">Network Error</h6>
                <p class="mb-0 small">Something went wrong while connecting to the server. Please try again.</p>
              </div>
            </div>
          `;
        }
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.innerHTML = `Submit Application <i class="bi bi-send-fill ms-1"></i>`;
        }
      });
  });
}

/* ==========================================================================
   3. Recruiter Dashboard & ATS Pipeline Live Status Changer
   ========================================================================== */
function initRecruiterDashboard() {
  const statusSelectors = document.querySelectorAll(".recruiter-status-select");
  const quickStatusBtns = document.querySelectorAll(".btn-quick-status");
  const candidateModalEl = document.getElementById("candidateDetailModal");

  // Candidate Details Modal trigger
  document.querySelectorAll(".btn-view-candidate").forEach((btn) => {
    btn.addEventListener("click", function () {
      const name = this.getAttribute("data-candidate-name");
      const email = this.getAttribute("data-candidate-email");
      const phone = this.getAttribute("data-candidate-phone");
      const portfolio = this.getAttribute("data-candidate-portfolio");
      const skills = this.getAttribute("data-candidate-skills");
      const jobTitle = this.getAttribute("data-job-title");
      const companyName = this.getAttribute("data-company-name");
      const coverLetter = this.getAttribute("data-cover-letter");
      const appliedDate = this.getAttribute("data-applied-date");
      const status = this.getAttribute("data-status");

      if (candidateModalEl) {
        document.getElementById("cdModalName").textContent = name;
        document.getElementById("cdModalEmail").textContent = email;
        document.getElementById("cdModalEmail").href = `mailto:${email}`;
        document.getElementById("cdModalPhone").textContent = phone;
        document.getElementById("cdModalJob").textContent = `${jobTitle} (${companyName})`;
        document.getElementById("cdModalSkills").textContent = skills;
        document.getElementById("cdModalDate").textContent = appliedDate;
        document.getElementById("cdModalCoverLetter").textContent = coverLetter;

        const portLink = document.getElementById("cdModalPortfolio");
        if (portfolio && portfolio.trim()) {
          portLink.href = portfolio;
          portLink.textContent = portfolio;
          portLink.parentElement.style.display = "";
        } else {
          portLink.parentElement.style.display = "none";
        }

        const badge = document.getElementById("cdModalStatusBadge");
        badge.textContent = status;
        badge.className = `badge ${getStatusBadgeClass(status)}`;

        const modal = bootstrap.Modal.getOrCreateInstance(candidateModalEl);
        modal.show();
      }
    });
  });

  // AJAX status changer
  function updateApplicationStatus(appId, newStatus) {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || "";

    return fetch(`/recruiter/applications/${appId}/status/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRFToken": csrfToken
      },
      body: JSON.stringify({ status: newStatus })
    })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          // Reload page to re-organize Kanban columns or update seamlessly
          window.location.reload();
        } else {
          alert("Could not update status: " + (data.message || "Unknown error"));
        }
      })
      .catch(err => {
        console.error("Status update error:", err);
        alert("An error occurred while updating the candidate status.");
      });
  }

  statusSelectors.forEach((sel) => {
    sel.addEventListener("change", function () {
      const appId = this.getAttribute("data-app-id");
      const newStatus = this.value;
      updateApplicationStatus(appId, newStatus);
    });
  });

  quickStatusBtns.forEach((btn) => {
    btn.addEventListener("click", function (e) {
      e.preventDefault();
      const appId = this.getAttribute("data-app-id");
      const newStatus = this.getAttribute("data-target-status");
      updateApplicationStatus(appId, newStatus);
    });
  });
}

function getStatusBadgeClass(status) {
  switch (status) {
    case "Applied": return "bg-primary";
    case "Under Review": return "bg-warning text-dark";
    case "Shortlisted": return "bg-success";
    case "Rejected": return "bg-danger";
    default: return "bg-secondary";
  }
}
