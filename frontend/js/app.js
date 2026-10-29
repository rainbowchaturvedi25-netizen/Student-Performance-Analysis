/**
 * Main Application Controller for All-Semesters CGPA & Campus Placement Evaluation.
 * Evaluates student marks across all 8 semesters, computes individual semester SGPA,
 * calculates Cumulative Average CGPA across all semesters, and determines campus placement
 * eligibility with visual traffic light status:
 *   🟢 GREEN LIGHT: Yes · Eligible for Placement (CGPA >= 7.0, 0 Backlogs)
 *   🟡 YELLOW LIGHT: Caution · Conditional Eligibility (CGPA 6.0 - 6.99 or 1 Backlog)
 *   🔴 RED LIGHT: No · Not Eligible for Placements (CGPA < 6.0 or Multiple Backlogs)
 *
 * Integrated with Persistent Local SQLite Database & Student Login Portal.
 */

document.addEventListener('DOMContentLoaded', async () => {
  window.perfCharts.initDefaults();

  // Application State
  const state = {
    currentUser: null,
    semestersData: null,
    activeSemesterNum: 1,
    activeSemester: null,
    currentSemester: 5,  // The semester the student is currently enrolled in
    attendance: 94.0,
    studyHours: 14.0,
    sleepHours: 8.0,
  };

  // DOM Elements Cache
  const els = {
    // Authentication & Login Portal
    authPortalOverlay: document.getElementById('auth-portal-overlay'),
    tabAuthLogin: document.getElementById('tab-auth-login'),
    tabAuthRegister: document.getElementById('tab-auth-register'),
    formAuthLogin: document.getElementById('form-auth-login'),
    formAuthRegister: document.getElementById('form-auth-register'),
    loginUsername: document.getElementById('login-username'),
    loginPassword: document.getElementById('login-password'),
    loginCurrentSemester: document.getElementById('login-current-semester'),
    regFullname: document.getElementById('reg-fullname'),
    regRollno: document.getElementById('reg-rollno'),
    regUsername: document.getElementById('reg-username'),
    regPassword: document.getElementById('reg-password'),
    regProgram: document.getElementById('reg-program'),
    regCurrentSemester: document.getElementById('reg-current-semester'),
    authAlert: document.getElementById('auth-alert'),
    btnLogout: document.getElementById('btn-logout'),

    // Header & Identity
    headerStudentName: document.getElementById('header-student-name'),
    headerStudentId: document.getElementById('header-student-id'),
    spStudentName: document.getElementById('sp-student-name'),
    spProgram: document.getElementById('sp-program'),
    apiStatusBadge: document.getElementById('api-status-badge'),
    apiLatencyText: document.getElementById('api-latency-text'),

    // Top Bento Ribbon KPIs
    ribbonAvgCgpa: document.getElementById('stat-cohort-avg'),
    ribbonPlacementStatus: document.getElementById('stat-pass-rate'),
    ribbonPlacementSub: document.getElementById('stat-pass-sub'),
    ribbonBacklogs: document.getElementById('stat-at-risk'),
    ribbonTotalSemesters: document.getElementById('stat-total-students'),

    // Traffic Light Lamps
    lampRed: document.getElementById('lamp-red'),
    lampYellow: document.getElementById('lamp-yellow'),
    lampGreen: document.getElementById('lamp-green'),

    // Placement Verdict Details
    placementVerdictBadge: document.getElementById('placement-verdict-badge'),
    placementSignalIcon: document.getElementById('placement-signal-icon'),
    placementVerdictText: document.getElementById('placement-verdict-text'),
    placementHeadline: document.getElementById('placement-headline'),
    placementSummary: document.getElementById('placement-summary'),
    placementCgpaVal: document.getElementById('placement-cgpa-val'),
    placementBacklogsVal: document.getElementById('placement-backlogs-val'),
    placementReadinessVal: document.getElementById('placement-readiness-val'),

    // Company Tier Badges
    badgeTier1: document.getElementById('badge-tier-1'),
    badgeTier2: document.getElementById('badge-tier-2'),
    badgeTier3: document.getElementById('badge-tier-3'),

    // Semester Selector & Subjects Container
    semesterPillsContainer: document.getElementById('semester-pills-container'),
    activeSemHeading: document.getElementById('active-sem-heading'),
    activeSemSgpaBadge: document.getElementById('active-sem-sgpa-badge'),
    semesterSubjectsContainer: document.getElementById('semester-subjects-container'),

    // Active Semester Result Card
    scoreVal: document.getElementById('res-score-val'),
    gaugeCircleFill: document.getElementById('gauge-circle-fill'),
    resStudentName: document.getElementById('res-student-name'),
    resFinalResultBadge: document.getElementById('res-final-result-badge'),
    resStudentId: document.getElementById('res-student-id'),
    resAcademicStatus: document.getElementById('res-academic-status'),
    resRiskBadge: document.getElementById('res-risk-badge'),
    resGradeLetter: document.getElementById('res-grade-letter'),
    resGpaVal: document.getElementById('res-gpa-val'),
    resTotalMarks: document.getElementById('res-total-marks'),
    resTopSubject: document.getElementById('res-top-subject'),

    // Placement Reasons & Action Plan Containers
    resDriversContainer: document.getElementById('res-drivers-container'),
    resRecContainer: document.getElementById('res-rec-container'),
    resSubjectsContainer: document.getElementById('res-subjects-container'),

    // Habit Inputs & Sliders
    attSlider: document.getElementById('slider-attendance'),
    attInput: document.getElementById('num-attendance'),
    badgeAtt: document.getElementById('badge-attendance'),
    hrsSlider: document.getElementById('slider-hours'),
    hrsInput: document.getElementById('num-hours'),
    badgeHrs: document.getElementById('badge-hours'),
    sleepSlider: document.getElementById('slider-sleep'),
    sleepInput: document.getElementById('num-sleep'),
    badgeSleep: document.getElementById('badge-sleep'),

    // Buttons
    btnAnalyze: document.getElementById('btn-run-analysis'),
    btnViewCurrentReport: document.getElementById('btn-view-current-report'),
    btnOpenEnterMarks: document.getElementById('btn-open-enter-marks'),
    btnMarksAddNew: document.getElementById('btn-marks-add-new'),

    // Modals
    modalReportCard: document.getElementById('modal-report-card'),
    btnCloseReportModal: document.getElementById('btn-close-report-modal'),
    btnDismissReport: document.getElementById('btn-dismiss-report'),
    btnPrintReport: document.getElementById('btn-print-report'),
    reportCardContent: document.getElementById('report-card-content'),

    // Tab 3 Ledger Table
    semestersLedgerTbody: document.getElementById('semesters-ledger-tbody'),
    marksSearch: document.getElementById('marks-search'),
    marksFilterStatus: document.getElementById('marks-filter-status'),

    // Telemetry Console
    consoleEndpoint: document.getElementById('console-endpoint'),
    consoleStatus: document.getElementById('console-status'),
    consoleLatency: document.getElementById('console-latency'),
    consoleReqJson: document.getElementById('console-req-json'),
    consoleResJson: document.getElementById('console-res-json'),
  };

  // --------------------------------------------------------------------------
  // Tab Switching Management
  // --------------------------------------------------------------------------
  document.querySelectorAll('.tab-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tab-btn').forEach((b) => b.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach((tc) => tc.classList.remove('active'));

      btn.classList.add('active');
      const targetId = btn.getAttribute('data-target');
      const targetTab = document.getElementById(targetId);
      if (targetTab) targetTab.classList.add('active');

      if (targetId === 'tab-growth' && state.semestersData) {
        window.perfCharts.renderGrowthCharts(state.semestersData);
      }
    });
  });

  document.querySelectorAll('.stat-card').forEach((card) => {
    card.addEventListener('click', () => {
      const targetId = card.getAttribute('data-target');
      if (targetId) {
        const btn = document.querySelector(`.tab-btn[data-target="${targetId}"]`);
        if (btn) btn.click();
      }
    });
  });

  // --------------------------------------------------------------------------
  // Authentication & Login Portal Handlers
  // --------------------------------------------------------------------------
  function showAuthAlert(msg, isSuccess = false) {
    if (!els.authAlert) return;
    els.authAlert.textContent = msg;
    els.authAlert.className = `auth-alert-box ${isSuccess ? 'success' : 'error'}`;
    els.authAlert.style.display = 'block';
  }

  function clearAuthAlert() {
    if (els.authAlert) els.authAlert.style.display = 'none';
  }

  // Toggle between Sign In & Register Tabs
  if (els.tabAuthLogin && els.tabAuthRegister) {
    els.tabAuthLogin.addEventListener('click', () => {
      els.tabAuthLogin.classList.add('active');
      els.tabAuthRegister.classList.remove('active');
      if (els.formAuthLogin) els.formAuthLogin.style.display = 'flex';
      if (els.formAuthRegister) els.formAuthRegister.style.display = 'none';
      clearAuthAlert();
    });

    els.tabAuthRegister.addEventListener('click', () => {
      els.tabAuthRegister.classList.add('active');
      els.tabAuthLogin.classList.remove('active');
      if (els.formAuthLogin) els.formAuthLogin.style.display = 'none';
      if (els.formAuthRegister) els.formAuthRegister.style.display = 'flex';
      clearAuthAlert();
    });
  }

  // Handle Login Form Submit
  if (els.formAuthLogin) {
    els.formAuthLogin.addEventListener('submit', async (e) => {
      e.preventDefault();
      clearAuthAlert();
      const u = els.loginUsername.value.trim();
      const p = els.loginPassword.value;
      const sem = els.loginCurrentSemester ? parseInt(els.loginCurrentSemester.value, 10) : 5;

      try {
        const user = await window.api.login(u, p, sem);
        onLoginSuccess(user);
      } catch (err) {
        showAuthAlert(err.message || 'Login failed. Please verify credentials.');
      }
    });
  }

  // Handle Registration Form Submit
  if (els.formAuthRegister) {
    els.formAuthRegister.addEventListener('submit', async (e) => {
      e.preventDefault();
      clearAuthAlert();
      const regData = {
        full_name: els.regFullname.value.trim(),
        student_id: els.regRollno.value.trim(),
        username: els.regUsername.value.trim(),
        password: els.regPassword.value,
        program: els.regProgram.value.trim() || 'B.Tech Computer Science & Engineering',
        batch: '2022 - 2026',
        current_semester: els.regCurrentSemester ? parseInt(els.regCurrentSemester.value, 10) : 5,
      };

      try {
        const user = await window.api.register(regData);
        showAuthAlert('Account created successfully! Launching portal...', true);
        setTimeout(() => onLoginSuccess(user), 600);
      } catch (err) {
        showAuthAlert(err.message || 'Registration failed.');
      }
    });
  }

  // Handle One-Click Demo Accounts
  document.querySelectorAll('.demo-pill-btn').forEach((btn) => {
    btn.addEventListener('click', async () => {
      const u = btn.getAttribute('data-demo-user');
      const p = btn.getAttribute('data-demo-pass');
      if (els.loginUsername) els.loginUsername.value = u;
      if (els.loginPassword) els.loginPassword.value = p;
      const sem = els.loginCurrentSemester ? parseInt(els.loginCurrentSemester.value, 10) : 5;
      try {
        const user = await window.api.login(u, p, sem);
        onLoginSuccess(user);
      } catch (err) {
        showAuthAlert(`Demo login failed: ${err.message}`);
      }
    });
  });

  // Handle Logout
  if (els.btnLogout) {
    els.btnLogout.addEventListener('click', () => {
      localStorage.removeItem('edumetric_active_user');
      state.currentUser = null;
      if (els.authPortalOverlay) {
        els.authPortalOverlay.classList.remove('hidden');
      }
      clearAuthAlert();
      if (els.loginUsername) els.loginUsername.focus();
    });
  }

  function onLoginSuccess(user) {
    state.currentUser = user;
    // Store current_semester from auth response (defaults to 5 if missing)
    state.currentSemester = user.current_semester || 5;
    localStorage.setItem('edumetric_active_user', JSON.stringify(user));

    if (els.authPortalOverlay) {
      els.authPortalOverlay.classList.add('hidden');
    }

    // Update Header & Identity
    if (els.headerStudentName) els.headerStudentName.textContent = user.full_name;
    if (els.headerStudentId) els.headerStudentId.textContent = `${user.student_id} · ${user.program.split(' ')[0]} CSE`;
    if (els.spStudentName) els.spStudentName.textContent = user.full_name;
    if (els.spProgram) els.spProgram.textContent = user.program;

    // Sync Groq panel semester selector with the student's current semester
    const groqSemSel = document.getElementById('groq-current-semester');
    if (groqSemSel) groqSemSel.value = String(state.currentSemester);

    // Load user's persistent 8-semesters marks from SQLite database
    loadUserSemesters(user.student_id).then(() => {
      if (typeof loadStudentAspirations === 'function') loadStudentAspirations(user.student_id);
    });
  }

  // --------------------------------------------------------------------------
  // Grade Point & Grade Letter Helpers (10-point scale)
  // --------------------------------------------------------------------------
  function marksToGpLetter(marks) {
    const m = Math.round(marks * 10) / 10;
    if (m >= 90) return { gp: 10, letter: 'O', css: 'o', pass: true };
    if (m >= 80) return { gp: 9, letter: 'A+', css: 'a', pass: true };
    if (m >= 70) return { gp: 8, letter: 'A', css: 'a', pass: true };
    if (m >= 60) return { gp: 7, letter: 'B+', css: 'b', pass: true };
    if (m >= 50) return { gp: 6, letter: 'B', css: 'b', pass: true };
    if (m >= 45) return { gp: 5, letter: 'C', css: 'b', pass: true };
    if (m >= 40) return { gp: 4, letter: 'P', css: 'b', pass: true };
    return { gp: 0, letter: 'F (Backlog)', css: 'f', pass: false };
  }

  // --------------------------------------------------------------------------
  // Placement Traffic Light Presentation Engine
  // --------------------------------------------------------------------------
  function computeFilteredPlacement(allData) {
    /**
     * Recomputes placement metrics using ONLY semesters up to state.currentSemester.
     * Returns a placement-like object with avg_cgpa, total_backlogs, light_color etc.
     */
    const currentSem = state.currentSemester || 8;
    const activeSems = (allData.semesters || []).filter(s => s.semester_num <= currentSem);

    if (activeSems.length === 0) return allData.placement;

    let totalWeighted = 0;
    let totalCredits = 0;
    let totalBacklogs = 0;
    let totalEarned = 0;

    activeSems.forEach(s => {
      const cr = s.credits_total || 20;
      totalWeighted += s.sgpa * cr;
      totalCredits += cr;
      totalBacklogs += s.backlogs_count || 0;
      totalEarned += s.credits_earned || 0;
    });

    const avgCgpa = totalCredits > 0 ? Math.round((totalWeighted / totalCredits) * 100) / 100 : 0;

    // Determine traffic light
    let lightColor, lightClass, lightLabel, eligible, status;
    if (totalBacklogs === 0 && avgCgpa >= 7.0) {
      lightColor = 'GREEN'; lightClass = 'green'; status = 'ELIGIBLE';
      lightLabel = 'YES · ELIGIBLE FOR CAMPUS PLACEMENTS';
      eligible = true;
    } else if (avgCgpa >= 6.0 && totalBacklogs <= 1) {
      lightColor = 'YELLOW'; lightClass = 'yellow'; status = 'CAUTION';
      lightLabel = 'CAUTION · CONDITIONAL ELIGIBILITY';
      eligible = false;
    } else {
      lightColor = 'RED'; lightClass = 'red'; status = 'INELIGIBLE';
      lightLabel = 'NO · NOT ELIGIBLE FOR PLACEMENTS';
      eligible = false;
    }

    const readiness = Math.min(100, Math.round(((avgCgpa / 10) * 70) + (totalBacklogs === 0 ? 20 : 0) + Math.min(10, activeSems.length * 1.25)));

    const tier1 = totalBacklogs === 0 && avgCgpa >= 8.0;
    const tier2 = totalBacklogs === 0 && avgCgpa >= 7.0;
    const tier3 = totalBacklogs <= 1 && avgCgpa >= 6.0;

    const semLabel = activeSems.length === 1 ? 'Semester 1' : `Semesters 1–${currentSem}`;
    const headline = lightColor === 'GREEN'
      ? `Cleared for Campus Placements — Based on ${semLabel}`
      : lightColor === 'YELLOW'
      ? `Conditional Eligibility — Improve CGPA to qualify — Based on ${semLabel}`
      : `Not Yet Eligible — Based on ${semLabel}`;

    const summary = lightColor === 'GREEN'
      ? `Avg CGPA ${avgCgpa.toFixed(2)}/10.0 across ${activeSems.length} completed semester(s). ${totalBacklogs === 0 ? 'No active backlogs.' : ''} On track for placements.`
      : lightColor === 'YELLOW'
      ? `Avg CGPA ${avgCgpa.toFixed(2)}/10.0 across ${activeSems.length} semester(s). Borderline — maintain ≥7.0 CGPA for full eligibility.`
      : `Avg CGPA ${avgCgpa.toFixed(2)}/10.0 with ${totalBacklogs} active backlog(s) across ${activeSems.length} semester(s). Clear arrears to improve eligibility.`;

    return {
      ...allData.placement,
      avg_cgpa: avgCgpa,
      total_backlogs: totalBacklogs,
      total_credits_earned: totalEarned,
      light_color: lightColor,
      light_class: lightClass,
      light_label: lightLabel,
      eligible,
      status,
      readiness_score: readiness,
      tier1_eligible: tier1,
      tier2_eligible: tier2,
      tier3_eligible: tier3,
      headline,
      summary,
      _filtered_sem_count: activeSems.length,
      _current_semester: currentSem,
    };
  }

  function renderPlacementTrafficLight(placement, allData) {
    if (!placement) return;

    // Always recompute placement based only on completed semesters
    const filteredPlacement = allData ? computeFilteredPlacement(allData) : placement;
    const p = filteredPlacement;

    if (els.lampRed) els.lampRed.classList.remove('active');
    if (els.lampYellow) els.lampYellow.classList.remove('active');
    if (els.lampGreen) els.lampGreen.classList.remove('active');

    const color = (p.light_color || 'GREEN').toUpperCase();

    if (color === 'RED') {
      if (els.lampRed) els.lampRed.classList.add('active');
    } else if (color === 'YELLOW') {
      if (els.lampYellow) els.lampYellow.classList.add('active');
    } else {
      if (els.lampGreen) els.lampGreen.classList.add('active');
    }

    if (els.placementVerdictBadge) {
      els.placementVerdictBadge.className = `placement-badge-banner ${p.light_class || 'green'}`;
      if (els.placementSignalIcon) {
        els.placementSignalIcon.textContent = color === 'GREEN' ? '🟢' : color === 'YELLOW' ? '🟡' : '🔴';
      }
      if (els.placementVerdictText) {
        els.placementVerdictText.textContent = p.light_label || 'PLACEMENT EVALUATION';
      }
    }

    if (els.placementHeadline) els.placementHeadline.textContent = p.headline;
    if (els.placementSummary) els.placementSummary.textContent = p.summary;

    if (els.placementCgpaVal) els.placementCgpaVal.textContent = p.avg_cgpa.toFixed(2);
    if (els.placementBacklogsVal) {
      els.placementBacklogsVal.textContent = p.total_backlogs;
      els.placementBacklogsVal.style.color = p.total_backlogs === 0 ? '#059669' : '#dc2626';
    }
    if (els.placementReadinessVal) {
      els.placementReadinessVal.textContent = `${p.readiness_score}%`;
      els.placementReadinessVal.style.color = p.readiness_score >= 80 ? '#4f46e5' : p.readiness_score >= 60 ? '#d97706' : '#dc2626';
    }

    if (els.ribbonAvgCgpa) els.ribbonAvgCgpa.textContent = `${p.avg_cgpa.toFixed(2)} / 10.0`;
    if (els.ribbonPlacementStatus) {
      els.ribbonPlacementStatus.textContent = color === 'GREEN' ? '🟢 ELIGIBLE' : color === 'YELLOW' ? '🟡 CAUTION' : '🔴 INELIGIBLE';
      els.ribbonPlacementStatus.style.color = color === 'GREEN' ? '#059669' : color === 'YELLOW' ? '#d97706' : '#dc2626';
    }
    if (els.ribbonPlacementSub) {
      const semFilterNote = p._current_semester ? ` · Sem 1–${p._current_semester}` : '';
      els.ribbonPlacementSub.innerHTML = `${color === 'GREEN' ? 'Green Light · Cleared for Placement' : color === 'YELLOW' ? 'Yellow Light · Conditional Eligibility' : 'Red Light · Not Eligible for Drives'}${semFilterNote} <span class="stat-click-hint">View Signal →</span>`;
    }
    if (els.ribbonBacklogs) {
      els.ribbonBacklogs.textContent = `${p.total_backlogs} Backlog${p.total_backlogs === 1 ? '' : 's'}`;
      els.ribbonBacklogs.style.color = p.total_backlogs === 0 ? '#059669' : '#dc2626';
    }
    if (els.ribbonTotalSemesters) {
      const currentSem = state.currentSemester || 8;
      els.ribbonTotalSemesters.textContent = `${currentSem} of 8 Semesters`;
    }

    // Add "Placement score based on Sem N" badge near the CGPA KPI
    const existingFilterBadge = document.getElementById('placement-sem-filter-badge');
    if (existingFilterBadge) existingFilterBadge.remove();
    if (p._current_semester && p._current_semester < 8) {
      const filterBadge = document.createElement('div');
      filterBadge.id = 'placement-sem-filter-badge';
      filterBadge.className = 'placement-sem-filter-badge';
      filterBadge.innerHTML = `📅 Score based on Semester 1–${p._current_semester} only`;
      if (els.placementCgpaVal && els.placementCgpaVal.parentNode) {
        els.placementCgpaVal.parentNode.appendChild(filterBadge);
      }
    }

    const updateTier = (badgeEl, isUnlocked) => {
      if (!badgeEl) return;
      badgeEl.textContent = isUnlocked ? 'UNLOCKED' : 'LOCKED';
      badgeEl.className = `tier-badge ${isUnlocked ? 'unlocked' : 'locked'}`;
    };
    updateTier(els.badgeTier1, p.tier1_eligible);
    updateTier(els.badgeTier2, p.tier2_eligible);
    updateTier(els.badgeTier3, p.tier3_eligible);

    if (els.resDriversContainer) {
      const reasons = p.reasons && p.reasons.length > 0 ? p.reasons : [p.summary];
      els.resDriversContainer.innerHTML = reasons.map(r => `
        <div class="driver-item" style="border-left: 3px solid ${color === 'GREEN' ? '#10b981' : color === 'YELLOW' ? '#f59e0b' : '#ef4444'}; padding: 0.6rem 0.9rem; background: #f8fafc; border-radius: 8px; margin-bottom: 0.5rem;">
          <div style="font-size: 0.85rem; font-weight: 600; color: #1e293b;">${r}</div>
        </div>
      `).join('');
    }

    if (els.resRecContainer) {
      const actions = p.action_plan && p.action_plan.length > 0 ? p.action_plan : ['Keep improving your CGPA each semester to strengthen your placement eligibility.'];
      els.resRecContainer.innerHTML = actions.map(a => `
        <li style="margin-bottom: 0.4rem; font-size: 0.85rem; color: #334155;">${a}</li>
      `).join('');
    }
  }

  // --------------------------------------------------------------------------
  // Semester Selector Navigation Ribbon
  // --------------------------------------------------------------------------
  function renderSemesterPills(semesters, activeNum) {
    if (!els.semesterPillsContainer || !semesters) return;
    els.semesterPillsContainer.innerHTML = '';

    const currentSem = state.currentSemester || 8;

    // Show or update the "active semester" banner above the pills
    let banner = document.getElementById('active-sem-portal-banner');
    if (!banner) {
      banner = document.createElement('div');
      banner.id = 'active-sem-portal-banner';
      banner.className = 'active-sem-banner';
      els.semesterPillsContainer.parentNode.insertBefore(banner, els.semesterPillsContainer);
    }
    banner.innerHTML = currentSem >= 8
      ? `<div class="asb-icon">🎓</div><div class="asb-text">You are enrolled in <strong>Final Semester 8</strong>. All 8 semesters are active for complete placement evaluation.</div>`
      : `<div class="asb-icon">📅</div><div class="asb-text">You are currently in <strong>Semester ${currentSem}</strong>. Semesters <strong>${currentSem + 1}–8</strong> are marked as <em>Upcoming</em> (locked). Placement confidence score is evaluated up to <strong>Semester ${currentSem}</strong>.</div>`;

    semesters.forEach((sem) => {
      const btn = document.createElement('button');
      btn.type = 'button';

      const isFuture = sem.semester_num > currentSem;
      const dotColor = isFuture ? 'gray'
        : (sem.backlogs_count > 0 || sem.sgpa < 6.0) ? 'red'
        : sem.sgpa < 7.0 ? 'yellow'
        : 'green';

      btn.className = `sem-pill-btn ${sem.semester_num === activeNum ? 'active' : ''} ${isFuture ? 'locked-upcoming' : ''}`;

      btn.innerHTML = isFuture
        ? `
          <span class="sem-title">Sem ${sem.semester_num}</span>
          <span class="sem-sgpa-text" style="color:#94a3b8;font-size:0.65rem;">Upcoming</span>
          <span class="sem-lock-icon">🔒</span>
        `
        : `
          <span class="sem-title">Sem ${sem.semester_num}</span>
          <span class="sem-sgpa-text">${sem.sgpa.toFixed(2)}</span>
          <span class="sem-status-dot ${dotColor}" title="${sem.status} (${sem.sgpa.toFixed(2)} SGPA)"></span>
        `;

      if (!isFuture) {
        btn.setAttribute('title', `Semester ${sem.semester_num} — SGPA: ${sem.sgpa.toFixed(2)} | ${sem.status}`);
        btn.addEventListener('click', () => {
          state.activeSemesterNum = sem.semester_num;
          renderSemesterPills(semesters, sem.semester_num);
          const currentSemObj = (state.semestersData && state.semestersData.semesters.find(s => s.semester_num === sem.semester_num)) || sem;
          renderActiveSemesterSubjects(currentSemObj);
        });
      } else {
        btn.setAttribute('title', `Semester ${sem.semester_num} — Upcoming (not yet enrolled)`);
        btn.setAttribute('disabled', 'true');
      }

      els.semesterPillsContainer.appendChild(btn);
    });
  }

  // --------------------------------------------------------------------------
  // Update Summary Badges, Gauge, and Mastery Bars without wiping inputs
  // --------------------------------------------------------------------------
  function updateActiveSemesterSummaryBadges(semester) {
    if (!semester) return;

    if (els.activeSemHeading) {
      els.activeSemHeading.innerHTML = `<span>📐</span> ${semester.semester_name} Subjects (10-Point Scale)`;
    }
    if (els.activeSemSgpaBadge) {
      els.activeSemSgpaBadge.textContent = `${semester.sgpa.toFixed(2)} / 10.0`;
    }

    if (els.scoreVal) els.scoreVal.textContent = semester.sgpa.toFixed(2);
    if (els.resGradeLetter) {
      const semGrade = semester.sgpa >= 9.0 ? 'O' : semester.sgpa >= 8.0 ? 'A+' : semester.sgpa >= 7.0 ? 'A' : semester.sgpa >= 6.0 ? 'B+' : semester.sgpa >= 5.0 ? 'B' : 'F';
      els.resGradeLetter.textContent = semGrade;
    }
    if (els.resGpaVal) els.resGpaVal.textContent = `SGPA ${semester.sgpa.toFixed(2)} / 10.0`;
    if (els.resStudentName) els.resStudentName.textContent = `${semester.semester_name} Evaluation`;
    if (els.resStudentId) els.resStudentId.textContent = `${semester.credits_earned}/${semester.credits_total} Credits Earned`;
    if (els.resAcademicStatus) {
      els.resAcademicStatus.textContent = semester.backlogs_count === 0 ? 'All Courses Cleared' : `⚠️ ${semester.backlogs_count} Active Arrear(s)`;
      els.resAcademicStatus.style.color = semester.backlogs_count === 0 ? '#059669' : '#dc2626';
    }
    if (els.resFinalResultBadge) {
      els.resFinalResultBadge.textContent = semester.status;
      els.resFinalResultBadge.className = `result-badge-pill ${semester.status === 'PASSED' ? 'pass' : 'fail'}`;
    }
    if (els.resTotalMarks) {
      els.resTotalMarks.textContent = `${Math.round(semester.total_marks)} / ${Math.round(semester.max_marks)}`;
    }
    if (els.resRiskBadge) {
      els.resRiskBadge.textContent = semester.sgpa >= 7.0 ? 'Honors Standing' : semester.sgpa >= 6.0 ? 'Borderline' : 'Remedial Required';
      els.resRiskBadge.style.background = semester.sgpa >= 7.0 ? '#ecfdf5' : semester.sgpa >= 6.0 ? '#fffbeb' : '#fef2f2';
      els.resRiskBadge.style.color = semester.sgpa >= 7.0 ? '#065f46' : semester.sgpa >= 6.0 ? '#92400e' : '#991b1b';
      els.resRiskBadge.style.borderColor = semester.sgpa >= 7.0 ? '#a7f3d0' : semester.sgpa >= 6.0 ? '#fde68a' : '#fecaca';
    }

    if (els.gaugeCircleFill) {
      const radius = 50;
      const circumference = 2 * Math.PI * radius;
      const offset = circumference - (semester.sgpa / 10.0) * circumference;
      els.gaugeCircleFill.style.strokeDasharray = `${circumference}`;
      els.gaugeCircleFill.style.strokeDashoffset = `${offset}`;
      els.gaugeCircleFill.style.stroke = semester.sgpa >= 7.0 ? '#10b981' : semester.sgpa >= 6.0 ? '#f59e0b' : '#ef4444';
    }

    if (els.resTopSubject && semester.subjects.length > 0) {
      const sortedSubs = [...semester.subjects].sort((a, b) => b.marks - a.marks);
      els.resTopSubject.textContent = `${sortedSubs[0].name} (${Math.round(sortedSubs[0].marks)})`;
    }

    if (els.resSubjectsContainer) {
      els.resSubjectsContainer.innerHTML = semester.subjects.map(s => {
        const pct = Math.round(s.marks);
        const col = pct >= 80 ? '#10b981' : pct >= 60 ? '#4f46e5' : pct >= 40 ? '#f59e0b' : '#ef4444';
        return `
          <div class="subject-row" style="margin-bottom: 0.6rem;">
            <div style="display: flex; justify-content: space-between; font-size: 0.8rem; margin-bottom: 0.2rem;">
              <span style="font-weight: 600;">${s.code} · ${s.name}</span>
              <span style="font-family: var(--font-mono); font-weight: 700; color: ${col};">${pct}% (${s.grade_letter})</span>
            </div>
            <div style="background: #e2e8f0; height: 7px; border-radius: 4px; overflow: hidden;">
              <div style="background: ${col}; width: ${pct}%; height: 100%; border-radius: 4px;"></div>
            </div>
          </div>
        `;
      }).join('');
    }

    if (window.perfCharts && window.perfCharts.renderRadar) {
      const avgM = semester.subjects.reduce((a, b) => a + b.marks, 0) / Math.max(1, semester.subjects.length);
      window.perfCharts.renderRadar('chart-student-radar', {
        attendance: state.attendance,
        exam_score: avgM,
        assignment_avg: avgM * 0.95,
        study_hours: state.studyHours,
        sleep_hours: state.sleepHours,
      });
    }
  }

  // --------------------------------------------------------------------------
  // Active Semester Subject Sliders & Marks Inputs (Local DB Linked)
  // --------------------------------------------------------------------------
  function renderActiveSemesterSubjects(semester) {
    if (!semester) return;
    state.activeSemester = semester;
    updateActiveSemesterSummaryBadges(semester);

    if (!els.semesterSubjectsContainer) return;
    els.semesterSubjectsContainer.innerHTML = '';

    semester.subjects.forEach((sub) => {
      const card = document.createElement('div');
      card.className = 'semester-subject-card';

      const gpInfo = marksToGpLetter(sub.marks);

      card.innerHTML = `
        <div class="sub-header-line">
          <div class="sub-code-name">
            <span class="sub-code-tag">${sub.code}</span>
            <span>${sub.name}</span>
          </div>
          <div class="sub-credits-gp">
            <span>${sub.credits} Credits</span> &nbsp;•&nbsp;
            <span id="gp-badge-${sub.code}" class="gp-pill ${gpInfo.css}">${gpInfo.gp} GP (${gpInfo.letter})</span>
          </div>
        </div>
        <div class="slider-container" style="display: flex; gap: 0.8rem; align-items: center;">
          <input id="slider-${sub.code}" class="sub-mark-slider" type="range" min="0" max="100" step="1" value="${Math.round(sub.marks)}" style="flex: 1;">
          <input id="num-${sub.code}" class="slider-val-input sub-mark-num" type="number" min="0" max="100" step="1" value="${Math.round(sub.marks)}" style="width: 75px; text-align: center; font-weight: 700;">
        </div>
      `;

      const slider = card.querySelector(`#slider-${sub.code}`);
      const numInput = card.querySelector(`#num-${sub.code}`);
      const gpBadge = card.querySelector(`#gp-badge-${sub.code}`);

      const handleMarkChange = (newVal) => {
        // Clear active preset buttons since marks have been customized
        document.querySelectorAll('.preset-pill').forEach(p => p.classList.remove('active'));

        const val = Math.max(0, Math.min(100, parseFloat(newVal) || 0));
        sub.marks = val;

        const updatedGp = marksToGpLetter(val);
        sub.grade_point = updatedGp.gp;
        sub.grade_letter = updatedGp.letter;
        sub.passed = updatedGp.pass;

        gpBadge.className = `gp-pill ${updatedGp.css}`;
        gpBadge.textContent = `${updatedGp.gp} GP (${updatedGp.letter})`;

        let totalWeighted = 0;
        let totalCr = 0;
        let bCount = 0;
        let totalObt = 0;
        semester.subjects.forEach(s => {
          totalWeighted += (s.credits * s.grade_point);
          totalCr += s.credits;
          totalObt += s.marks;
          if (!s.passed) bCount++;
        });
        semester.sgpa = Math.round((totalWeighted / Math.max(1, totalCr)) * 100) / 100;
        semester.backlogs_count = bCount;
        semester.status = bCount > 0 ? 'BACKLOG' : 'PASSED';
        semester.total_marks = totalObt;
        semester.percentage = Math.round((totalObt / Math.max(1, semester.max_marks || 500)) * 1000) / 10;

        updateActiveSemesterSummaryBadges(semester);

        // Update pill display for current semester
        if (state.semestersData) {
          renderSemesterPills(state.semestersData.semesters, state.activeSemesterNum);
        }

        // Sync with SQLite database (debounced)
        debouncedSaveMarks(semester.semester_num);
      };

      slider.addEventListener('input', () => {
        numInput.value = slider.value;
        handleMarkChange(slider.value);
      });

      numInput.addEventListener('input', () => {
        slider.value = numInput.value;
        handleMarkChange(numInput.value);
      });

      els.semesterSubjectsContainer.appendChild(card);
    });
  }

  // Immediate or Debounced database sync for marks sliders & calculation
  let saveMarksTimer = null;
  async function syncAndRecalculateMarks(semesterNum, isImmediate = false) {
    if (!state.semestersData) return;

    // Grab marks directly from live inputs if this is the active semester on screen
    const marksPayload = {};
    if (state.activeSemester && state.activeSemester.semester_num === semesterNum) {
      state.activeSemester.subjects.forEach(s => {
        const slider = document.getElementById(`slider-${s.code}`);
        const numInput = document.getElementById(`num-${s.code}`);
        const val = numInput && numInput.value !== '' ? parseFloat(numInput.value) : (slider ? parseFloat(slider.value) : s.marks);
        s.marks = isNaN(val) ? s.marks : Math.max(0, Math.min(100, val));
        marksPayload[s.code] = s.marks;
      });
    } else {
      const targetSem = state.semestersData.semesters.find(s => s.semester_num === semesterNum);
      if (!targetSem) return;
      targetSem.subjects.forEach(s => {
        marksPayload[s.code] = s.marks;
      });
    }

    const sId = state.currentUser ? state.currentUser.student_id : 'STU-2026';

    try {
      const updatedData = await window.api.updateSemesterMarks(semesterNum, marksPayload, sId);
      state.semestersData = updatedData;

      // Keep activeSemester pointing to the updated object in updatedData
      const updatedActiveSem = updatedData.semesters.find(s => s.semester_num === state.activeSemesterNum)
        || updatedData.semesters[0];
      state.activeSemester = updatedActiveSem;

      renderPlacementTrafficLight(updatedData.placement, updatedData);
      renderSemesterPills(updatedData.semesters, state.activeSemesterNum);
      updateActiveSemesterSummaryBadges(updatedActiveSem); // DO NOT wipe sliders!
      renderAllSemestersLedger(updatedData.semesters, updatedData.avg_cgpa);

      if (window.perfCharts) {
        window.perfCharts.renderGrowthCharts(updatedData);
      }
      return updatedData;
    } catch (err) {
      console.error('Failed to save marks to local database:', err);
      throw err;
    }
  }

  function debouncedSaveMarks(semesterNum) {
    clearTimeout(saveMarksTimer);
    saveMarksTimer = setTimeout(() => {
      syncAndRecalculateMarks(semesterNum, false).catch(() => {});
    }, 400);
  }

  // --------------------------------------------------------------------------
  // Tab 3: All-Semesters Cumulative Ledger Table
  // --------------------------------------------------------------------------
  function renderAllSemestersLedger(semesters, avgCgpa) {
    if (!els.semestersLedgerTbody || !semesters) return;
    els.semestersLedgerTbody.innerHTML = '';

    const filterStatus = els.marksFilterStatus ? els.marksFilterStatus.value : 'all';
    const searchQuery = (els.marksSearch && els.marksSearch.value.trim().toLowerCase()) || '';

    semesters.forEach((sem) => {
      if (filterStatus === 'PASS' && sem.status !== 'PASSED') return;
      if (filterStatus === 'FAIL' && sem.status !== 'BACKLOG') return;

      if (searchQuery) {
        const matchesName = sem.semester_name.toLowerCase().includes(searchQuery);
        const matchesCourses = sem.subjects.some(s => s.name.toLowerCase().includes(searchQuery) || s.code.toLowerCase().includes(searchQuery));
        if (!matchesName && !matchesCourses) return;
      }

      const tr = document.createElement('tr');
      const isBacklog = sem.backlogs_count > 0;
      const statusClass = isBacklog ? 'backlog' : 'pass';
      const statusText = isBacklog ? `⚠️ ${sem.backlogs_count} Arrear(s)` : '✅ Cleared';

      tr.innerHTML = `
        <td><strong>${sem.semester_name}</strong></td>
        <td>${sem.subjects.length} Courses</td>
        <td>${Math.round(sem.total_marks)} / ${Math.round(sem.max_marks)}</td>
        <td><strong style="color: #4338ca;">${sem.percentage}%</strong></td>
        <td><strong style="font-family: var(--font-mono); font-size: 0.95rem; color: ${sem.sgpa >= 7.0 ? '#059669' : sem.sgpa >= 6.0 ? '#d97706' : '#dc2626'};">${sem.sgpa.toFixed(2)}</strong></td>
        <td>${sem.credits_earned} / ${sem.credits_total} Cr</td>
        <td><span style="color: ${isBacklog ? '#dc2626' : '#059669'}; font-weight: 700;">${sem.backlogs_count}</span></td>
        <td><span class="sem-table-badge ${statusClass}">${statusText}</span></td>
        <td>
          <button class="btn-ghost btn-table-view-sem" data-sem="${sem.semester_num}" style="padding: 0.25rem 0.65rem; font-size: 0.78rem;">
            Edit / View →
          </button>
        </td>
      `;

      tr.querySelector('.btn-table-view-sem').addEventListener('click', () => {
        state.activeSemesterNum = sem.semester_num;
        const tab1Btn = document.querySelector('.tab-btn[data-target="tab-sandbox"]');
        if (tab1Btn) tab1Btn.click();
        renderSemesterPills(semesters, sem.semester_num);
        renderActiveSemesterSubjects(sem);
        window.scrollTo({ top: 0, behavior: 'smooth' });
      });

      els.semestersLedgerTbody.appendChild(tr);
    });

    const statAvg = document.getElementById('marks-stat-avg');
    const statVerdict = document.getElementById('marks-stat-high-low');
    const statArrears = document.getElementById('marks-stat-pass-rate');
    const statTotal = document.getElementById('marks-stat-passed-failed');

    if (statAvg) statAvg.textContent = `${avgCgpa.toFixed(2)} / 10.0`;
    if (statVerdict && state.semestersData) {
      const pl = state.semestersData.placement;
      statVerdict.textContent = pl.light_color === 'GREEN' ? '🟢 Green Light (Eligible)' : pl.light_color === 'YELLOW' ? '🟡 Yellow Light (Caution)' : '🔴 Red Light (Ineligible)';
      statVerdict.style.color = pl.light_color === 'GREEN' ? '#059669' : pl.light_color === 'YELLOW' ? '#d97706' : '#dc2626';
    }
    if (statArrears && state.semestersData) {
      statArrears.textContent = `${state.semestersData.total_backlogs} Backlog(s)`;
      statArrears.style.color = state.semestersData.total_backlogs === 0 ? '#059669' : '#dc2626';
    }
    if (statTotal && state.semestersData) {
      statTotal.textContent = `${state.semestersData.total_semesters} Semesters (${state.semestersData.total_credits} Cr)`;
    }
  }

  if (els.marksSearch) {
    els.marksSearch.addEventListener('input', () => {
      if (state.semestersData) renderAllSemestersLedger(state.semestersData.semesters, state.semestersData.avg_cgpa);
    });
  }

  if (els.marksFilterStatus) {
    els.marksFilterStatus.addEventListener('change', () => {
      if (state.semestersData) renderAllSemestersLedger(state.semestersData.semesters, state.semestersData.avg_cgpa);
    });
  }

  // --------------------------------------------------------------------------
  // Benchmark Presets (Green, Yellow, Red Placement Lights)
  // --------------------------------------------------------------------------
  async function applyPreset(presetKey) {
    const sId = state.currentUser ? state.currentUser.student_id : 'STU-2026';
    try {
      if (els.btnAnalyze) {
        els.btnAnalyze.disabled = true;
        els.btnAnalyze.innerHTML = `<span>⏳</span> Applying ${presetKey.toUpperCase()} Benchmark...`;
      }

      const updated = await window.api.loadSemesterPreset(presetKey, sId);
      state.semestersData = updated;

      const activeSem = updated.semesters.find(s => s.semester_num === state.activeSemesterNum) || updated.semesters[0];
      state.activeSemester = activeSem;
      state.activeSemesterNum = activeSem.semester_num;

      renderPlacementTrafficLight(updated.placement, updated);
      renderSemesterPills(updated.semesters, state.activeSemesterNum);
      renderActiveSemesterSubjects(activeSem);
      renderAllSemestersLedger(updated.semesters, updated.avg_cgpa);

      if (window.perfCharts) {
        window.perfCharts.renderGrowthCharts(updated);
      }
    } catch (err) {
      console.error('Failed to apply preset:', err);
      alert(`Preset failed: ${err.message}`);
    } finally {
      if (els.btnAnalyze) {
        els.btnAnalyze.disabled = false;
        els.btnAnalyze.innerHTML = `<span>⚡</span> Recalculate SGPA & Placement Verdict`;
      }
    }
  }

  document.querySelectorAll('.preset-pill').forEach((pill) => {
    pill.addEventListener('click', () => {
      document.querySelectorAll('.preset-pill').forEach((p) => p.classList.remove('active'));
      pill.classList.add('active');
      const presetKey = pill.getAttribute('data-preset');
      applyPreset(presetKey);
    });
  });

  const form = document.getElementById('sandbox-form');
  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      clearTimeout(saveMarksTimer);

      const submitBtn = els.btnAnalyze || document.getElementById('btn-run-analysis');
      const originalHtml = submitBtn ? submitBtn.innerHTML : '';

      try {
        if (submitBtn) {
          submitBtn.disabled = true;
          submitBtn.innerHTML = `<span>⏳</span> Recalculating SGPA & Placement Verdict...`;
        }

        if (state.activeSemester) {
          await syncAndRecalculateMarks(state.activeSemester.semester_num, true);
        } else if (state.semestersData) {
          await syncAndRecalculateMarks(state.activeSemesterNum || 1, true);
        }

        // Also trigger Radar Chart update with updated habits
        if (window.perfCharts && window.perfCharts.renderRadar && state.activeSemester) {
          const avgM = state.activeSemester.subjects.reduce((a, b) => a + b.marks, 0) / Math.max(1, state.activeSemester.subjects.length);
          window.perfCharts.renderRadar('chart-student-radar', {
            attendance: state.attendance,
            exam_score: avgM,
            assignment_avg: avgM * 0.95,
            study_hours: state.studyHours,
            sleep_hours: state.sleepHours,
          });
        }

        if (submitBtn) {
          submitBtn.innerHTML = `<span>✅</span> Recalculated & Synced!`;
          submitBtn.style.background = 'linear-gradient(135deg, #059669 0%, #10b981 100%)';
          setTimeout(() => {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalHtml || `<span>⚡</span> Recalculate SGPA & Placement Verdict`;
            submitBtn.style.background = '';
          }, 1200);
        }
      } catch (err) {
        console.error('Recalculation error:', err);
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.innerHTML = `<span>⚠️</span> Error Recalculating`;
          setTimeout(() => {
            submitBtn.innerHTML = originalHtml || `<span>⚡</span> Recalculate SGPA & Placement Verdict`;
          }, 1500);
        }
      }
    });
  }

  const bindHabit = (slider, input, badge, suffix, stateKey) => {
    if (!slider || !input) return;
    slider.addEventListener('input', () => {
      input.value = slider.value;
      if (badge) badge.textContent = `${slider.value}${suffix}`;
      state[stateKey] = parseFloat(slider.value) || 0;
    });
    input.addEventListener('input', () => {
      slider.value = input.value;
      if (badge) badge.textContent = `${input.value}${suffix}`;
      state[stateKey] = parseFloat(input.value) || 0;
    });
  };

  bindHabit(els.attSlider, els.attInput, els.badgeAtt, '%', 'attendance');
  bindHabit(els.hrsSlider, els.hrsInput, els.badgeHrs, ' hrs', 'studyHours');
  bindHabit(els.sleepSlider, els.sleepInput, els.badgeSleep, ' hrs', 'sleepHours');

  // --------------------------------------------------------------------------
  // Official Consolidated Transcript & Placement Certificate Modal
  // --------------------------------------------------------------------------
  function openTranscriptModal() {
    if (!state.semestersData) return;
    const data = state.semestersData;
    const pl = data.placement;

    const stampText = pl.light_color === 'GREEN' ? 'PLACEMENT VERIFIED · ELIGIBLE' : pl.light_color === 'YELLOW' ? 'CONDITIONAL · CAUTION' : 'DISQUALIFIED · ARREARS';
    const stampColor = pl.light_color === 'GREEN' ? '#059669' : pl.light_color === 'YELLOW' ? '#d97706' : '#dc2626';

    if (els.reportCardContent) {
      els.reportCardContent.innerHTML = `
        <div class="transcript-seal-header" style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #e2e8f0; padding-bottom: 1rem; margin-bottom: 1.2rem;">
          <div>
            <h2 style="font-family: var(--font-display); font-size: 1.4rem; color: #0f172a;">Official Academic Transcript & Campus Placement Clearance</h2>
            <div style="font-size: 0.85rem; color: #64748b; margin-top: 0.2rem;">
              Candidate: <strong>${data.student_name}</strong> &nbsp;•&nbsp; Roll No: <strong>${data.student_id}</strong> &nbsp;•&nbsp; Program: <strong>${data.program}</strong>
            </div>
          </div>
          <div style="text-align: right;">
            <div style="border: 2.5px solid ${stampColor}; color: ${stampColor}; padding: 0.45rem 1rem; border-radius: 8px; font-weight: 900; font-family: var(--font-display); font-size: 0.88rem; letter-spacing: 0.05em; text-transform: uppercase;">
              ${stampText}
            </div>
          </div>
        </div>

        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.8rem; margin-bottom: 1.2rem; background: #f8fafc; padding: 0.9rem; border-radius: 12px; border: 1px solid #e2e8f0;">
          <div style="text-align: center;">
            <div style="font-size: 0.72rem; color: #64748b; font-weight: 700; text-transform: uppercase;">Cumulative Avg CGPA</div>
            <div style="font-size: 1.6rem; font-weight: 900; color: #4f46e5; font-family: var(--font-display);">${data.avg_cgpa.toFixed(2)} / 10.0</div>
          </div>
          <div style="text-align: center;">
            <div style="font-size: 0.72rem; color: #64748b; font-weight: 700; text-transform: uppercase;">Placement Signal</div>
            <div style="font-size: 1.2rem; font-weight: 900; color: ${stampColor}; font-family: var(--font-display); margin-top: 0.3rem;">${pl.light_label}</div>
          </div>
          <div style="text-align: center;">
            <div style="font-size: 0.72rem; color: #64748b; font-weight: 700; text-transform: uppercase;">Total Credits Earned</div>
            <div style="font-size: 1.4rem; font-weight: 800; color: #0f172a; font-family: var(--font-mono); margin-top: 0.2rem;">${data.total_credits} Cr</div>
          </div>
          <div style="text-align: center;">
            <div style="font-size: 0.72rem; color: #64748b; font-weight: 700; text-transform: uppercase;">Active Arrears</div>
            <div style="font-size: 1.4rem; font-weight: 800; color: ${data.total_backlogs === 0 ? '#059669' : '#dc2626'}; font-family: var(--font-mono); margin-top: 0.2rem;">${data.total_backlogs}</div>
          </div>
        </div>

        <h4 style="font-size: 0.95rem; font-weight: 700; color: #334155; margin-bottom: 0.6rem;">Consolidated 8-Semester Performance Ledger:</h4>
        <div style="overflow-x: auto; margin-bottom: 1.2rem;">
          <table class="roster-table marks-table" style="width: 100%; border-collapse: collapse;">
            <thead>
              <tr style="background: #f1f5f9;">
                <th style="padding: 8px 10px; text-align: left;">Semester</th>
                <th style="padding: 8px 10px; text-align: left;">Courses</th>
                <th style="padding: 8px 10px; text-align: center;">Total (/500)</th>
                <th style="padding: 8px 10px; text-align: center;">Percentage</th>
                <th style="padding: 8px 10px; text-align: center;">SGPA (/10.0)</th>
                <th style="padding: 8px 10px; text-align: center;">Credits</th>
                <th style="padding: 8px 10px; text-align: center;">Arrears</th>
                <th style="padding: 8px 10px; text-align: center;">Result</th>
              </tr>
            </thead>
            <tbody>
              ${data.semesters.map(s => `
                <tr style="border-bottom: 1px solid #e2e8f0;">
                  <td style="padding: 8px 10px; font-weight: 700;">${s.semester_name}</td>
                  <td style="padding: 8px 10px; font-size: 0.8rem; color: #475569;">${s.subjects.map(sub => sub.code).join(', ')}</td>
                  <td style="padding: 8px 10px; text-align: center;">${Math.round(s.total_marks)}</td>
                  <td style="padding: 8px 10px; text-align: center; font-weight: 600;">${s.percentage}%</td>
                  <td style="padding: 8px 10px; text-align: center; font-weight: 800; font-family: var(--font-mono); color: ${s.sgpa >= 7.0 ? '#059669' : s.sgpa >= 6.0 ? '#d97706' : '#dc2626'};">${s.sgpa.toFixed(2)}</td>
                  <td style="padding: 8px 10px; text-align: center;">${s.credits_earned}/${s.credits_total}</td>
                  <td style="padding: 8px 10px; text-align: center; font-weight: 700; color: ${s.backlogs_count > 0 ? '#dc2626' : '#059669'};">${s.backlogs_count}</td>
                  <td style="padding: 8px 10px; text-align: center;"><span class="sem-table-badge ${s.status === 'PASSED' ? 'pass' : 'backlog'}">${s.status}</span></td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>

        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1rem;">
          <h4 style="font-size: 0.9rem; font-weight: 800; color: #0f172a; margin-bottom: 0.4rem;">Placement Verification Audit:</h4>
          <p style="font-size: 0.84rem; color: #475569; line-height: 1.5; margin-bottom: 0.6rem;">${pl.summary}</p>
          <div style="display: flex; gap: 1rem; font-size: 0.82rem; font-weight: 600;">
            <span style="color: ${pl.tier1_eligible ? '#059669' : '#94a3b8'};">✦ Tier 1 Dream Tech: ${pl.tier1_eligible ? 'ELIGIBLE' : 'LOCKED'}</span>
            <span style="color: ${pl.tier2_eligible ? '#059669' : '#94a3b8'};">✦ Tier 2 Core Engineering: ${pl.tier2_eligible ? 'ELIGIBLE' : 'LOCKED'}</span>
            <span style="color: ${pl.tier3_eligible ? '#059669' : '#94a3b8'};">✦ Tier 3 IT Mass Recruiters: ${pl.tier3_eligible ? 'ELIGIBLE' : 'LOCKED'}</span>
          </div>
        </div>
      `;
    }

    if (els.modalReportCard) els.modalReportCard.classList.add('active');
  }

  if (els.btnViewCurrentReport) els.btnViewCurrentReport.addEventListener('click', openTranscriptModal);
  if (els.btnOpenEnterMarks) els.btnOpenEnterMarks.addEventListener('click', openTranscriptModal);
  if (els.btnMarksAddNew) els.btnMarksAddNew.addEventListener('click', openTranscriptModal);

  if (els.btnCloseReportModal) {
    els.btnCloseReportModal.addEventListener('click', () => {
      if (els.modalReportCard) els.modalReportCard.classList.remove('active');
    });
  }

  if (els.btnDismissReport) {
    els.btnDismissReport.addEventListener('click', () => {
      if (els.modalReportCard) els.modalReportCard.classList.remove('active');
    });
  }

  if (els.btnPrintReport) {
    els.btnPrintReport.addEventListener('click', () => {
      window.print();
    });
  }

  // --------------------------------------------------------------------------
  // API Live Telemetry Inspector
  // --------------------------------------------------------------------------
  window.api.onTelemetryUpdate((telemetry) => {
    if (els.apiStatusBadge) {
      els.apiStatusBadge.classList.add('online');
    }
    if (els.apiLatencyText) {
      els.apiLatencyText.textContent = `${telemetry.durationMs}ms`;
    }
    if (els.consoleEndpoint) {
      els.consoleEndpoint.textContent = `${telemetry.method} ${telemetry.endpoint}`;
      els.consoleEndpoint.className = `method-tag ${telemetry.method.toLowerCase()}`;
    }
    if (els.consoleStatus) {
      els.consoleStatus.textContent = telemetry.success ? `${telemetry.status} OK` : `${telemetry.status} ERROR`;
      els.consoleStatus.style.color = telemetry.success ? '#059669' : '#dc2626';
    }
    if (els.consoleLatency) {
      els.consoleLatency.textContent = `${telemetry.durationMs} ms (${telemetry.timestamp})`;
    }
    if (els.consoleReqJson) {
      els.consoleReqJson.textContent = telemetry.requestPayload
        ? JSON.stringify(telemetry.requestPayload, null, 2)
        : '// No request body (GET request)';
    }
    if (els.consoleResJson) {
      els.consoleResJson.textContent = telemetry.responsePayload
        ? JSON.stringify(telemetry.responsePayload, null, 2)
        : '// Empty response';
    }
  });

  // --------------------------------------------------------------------------
  // Load User Data & Application Startup
  // --------------------------------------------------------------------------
  async function loadUserSemesters(studentId) {
    try {
      const allSemestersData = await window.api.getAllSemesters(studentId);
      state.semestersData = allSemestersData;

      // Default active semester to the student's current enrolled semester (capped to available)
      const currentSem = state.currentSemester || 5;
      const defaultActiveNum = Math.min(currentSem, allSemestersData.semesters.length);
      state.activeSemesterNum = allSemestersData.active_semester || defaultActiveNum;

      const activeSem = allSemestersData.semesters.find(s => s.semester_num === state.activeSemesterNum)
        || allSemestersData.semesters[defaultActiveNum - 1]
        || allSemestersData.semesters[0];
      state.activeSemester = activeSem;

      renderPlacementTrafficLight(allSemestersData.placement, allSemestersData);
      renderSemesterPills(allSemestersData.semesters, state.activeSemesterNum);
      renderActiveSemesterSubjects(activeSem);
      renderAllSemestersLedger(allSemestersData.semesters, allSemestersData.avg_cgpa);

      if (window.perfCharts) {
        window.perfCharts.renderGrowthCharts(allSemestersData);
      }
    } catch (err) {
      console.error('Failed to load student semester data:', err);
    }
  }

  async function initApp() {
    try {
      await window.api.healthCheck();

      // Check saved authentication session
      const savedUserStr = localStorage.getItem('edumetric_active_user');
      if (savedUserStr) {
        try {
          const user = JSON.parse(savedUserStr);
          state.currentUser = user;
          // Restore current_semester from saved session
          state.currentSemester = user.current_semester || 5;

          if (els.authPortalOverlay) els.authPortalOverlay.classList.add('hidden');
          if (els.headerStudentName) els.headerStudentName.textContent = user.full_name;
          if (els.headerStudentId) els.headerStudentId.textContent = `${user.student_id} · ${user.program.split(' ')[0]} CSE`;
          if (els.spStudentName) els.spStudentName.textContent = user.full_name;
          if (els.spProgram) els.spProgram.textContent = user.program;

          // Sync login form semester selector to saved value
          if (els.loginCurrentSemester) els.loginCurrentSemester.value = String(state.currentSemester);
          const groqSemSel = document.getElementById('groq-current-semester');
          if (groqSemSel) groqSemSel.value = String(state.currentSemester);

          await loadUserSemesters(user.student_id);
          return;
        } catch (e) {
          localStorage.removeItem('edumetric_active_user');
        }
      }

      // No saved session -> Show Login Portal
      if (els.authPortalOverlay) {
        els.authPortalOverlay.classList.remove('hidden');
      }
      // Also load default preview in background
      state.currentSemester = 8; // show all semesters for demo
      await loadUserSemesters('STU-2026');
    } catch (err) {
      console.error('Initialization error:', err);
    }
  }

  // --------------------------------------------------------------------------
  // Groq AI Career & Placement Intelligence Panel
  // --------------------------------------------------------------------------

  /** Render coloured skill chip tags into a container */
  function renderSkillTags(container, skills, type = 'neutral') {
    if (!container) return;
    container.innerHTML = '';
    if (!skills || skills.length === 0) {
      container.innerHTML = `<span style="font-size:0.8rem;color:var(--text-muted);font-style:italic;">None listed</span>`;
      return;
    }
    skills.forEach((skill) => {
      const chip = document.createElement('span');
      chip.className = `groq-skill-tag ${type}`;
      const icon = type === 'match' ? '✓' : type === 'missing' ? '✗' : '·';
      chip.textContent = `${icon} ${skill}`;
      container.appendChild(chip);
    });
  }

  /** Animate number counter from 0 → target (for confidence & skill match) */
  function animateNumber(el, target, suffix = '%', duration = 900) {
    if (!el) return;
    const start = performance.now();
    const from = 0;
    const update = (now) => {
      const elapsed = now - start;
      const progress = Math.min(elapsed / duration, 1);
      const ease = 1 - Math.pow(1 - progress, 3); // cubic ease-out
      el.textContent = `${Math.round(from + (target - from) * ease)}${suffix}`;
      if (progress < 1) requestAnimationFrame(update);
    };
    requestAnimationFrame(update);
  }

  /** Render the full Groq AI analysis result into the panel */
  function renderGroqAnalysisResult(result) {
    const panel = document.getElementById('groq-analysis-results');
    if (!panel) return;
    panel.style.display = 'block';

    // Confidence score
    const confNum = document.getElementById('groq-confidence-num');
    const confBar = document.getElementById('groq-confidence-bar');
    const conf = Math.max(0, Math.min(100, result.confidence_score || 0));
    animateNumber(confNum, conf, '%');
    if (confBar) {
      setTimeout(() => { confBar.style.width = `${conf}%`; }, 50);
      // Color the bar
      const barColor = conf >= 70 ? 'linear-gradient(90deg,#4f46e5,#7c3aed)'
        : conf >= 50 ? 'linear-gradient(90deg,#d97706,#f59e0b)'
        : 'linear-gradient(90deg,#dc2626,#ef4444)';
      confBar.style.background = barColor;
    }

    // Skill match %
    const smNum = document.getElementById('groq-skillmatch-num');
    const smBar = document.getElementById('groq-skillmatch-bar');
    const sm = Math.max(0, Math.min(100, result.skill_match_percent || 0));
    animateNumber(smNum, sm, '%');
    if (smBar) {
      setTimeout(() => { smBar.style.width = `${sm}%`; }, 50);
      smBar.style.background = sm >= 60 ? '#10b981' : sm >= 40 ? '#f59e0b' : '#ef4444';
    }

    // On-track badge
    const trackBadge = document.getElementById('groq-ontrack-badge');
    const roleFit = document.getElementById('groq-role-fit');
    if (trackBadge) {
      const status = (result.on_track_status || 'NEEDS ATTENTION').toUpperCase();
      const cssClass = status.includes('ON TRACK') ? 'ontrack'
        : status.includes('RISK') || status.includes('AT RISK') ? 'at-risk'
        : 'needs-attention';
      trackBadge.textContent = status;
      trackBadge.className = `groq-ontrack-badge ${cssClass}`;
    }
    if (roleFit) {
      roleFit.textContent = result.role_fit_verdict || 'Analysing role fit…';
    }

    // Matching skills
    renderSkillTags(document.getElementById('groq-matching-skills'), result.matching_skills || [], 'match');

    // Missing skills
    renderSkillTags(document.getElementById('groq-missing-skills'), result.missing_critical_skills || [], 'missing');

    // Semester Roadmap
    const roadmapList = document.getElementById('groq-roadmap-list');
    if (roadmapList) {
      roadmapList.innerHTML = '';
      const steps = result.semester_roadmap || [];
      if (steps.length === 0) {
        roadmapList.innerHTML = `<li class="groq-roadmap-item">Keep up consistent academic performance and skill-building.</li>`;
      } else {
        steps.forEach((step) => {
          const li = document.createElement('li');
          li.className = 'groq-roadmap-item';
          li.textContent = step;
          roadmapList.appendChild(li);
        });
      }
    }

    // Interview Readiness
    const readinessEl = document.getElementById('groq-interview-readiness');
    if (readinessEl) {
      readinessEl.textContent = result.interview_readiness || 'No interview readiness notes available.';
    }

    // Scroll into view smoothly
    panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }

  /** Pre-fill the Groq panel inputs from saved aspirations in the DB */
  async function loadStudentAspirations(studentId) {
    try {
      const asp = await window.api.getStudentAspirations(studentId);
      if (!asp) return;

      const semSel = document.getElementById('groq-current-semester');
      const roleInput = document.getElementById('groq-desired-role');
      const skillsInput = document.getElementById('groq-skills-input');

      if (semSel && asp.current_semester) semSel.value = String(asp.current_semester);
      if (roleInput && asp.desired_role) roleInput.value = asp.desired_role;
      if (skillsInput && asp.skills && asp.skills.length > 0) {
        skillsInput.value = asp.skills.join(', ');
      }
    } catch (err) {
      // Silently ignore — student may not have aspirations saved yet
    }
  }

  /** Gather form values and call the Groq API */
  async function runGroqAnalysis() {
    const btn = document.getElementById('btn-run-groq-analysis');
    const icon = document.getElementById('groq-btn-icon');
    const text = document.getElementById('groq-btn-text');
    const spinner = document.getElementById('groq-btn-spinner');

    const semSel = document.getElementById('groq-current-semester');
    const roleInput = document.getElementById('groq-desired-role');
    const skillsInput = document.getElementById('groq-skills-input');

    const currentSemester = parseInt(semSel ? semSel.value : '5', 10);
    const desiredRole = (roleInput ? roleInput.value.trim() : '') || 'Software Developer';
    const skillsRaw = skillsInput ? skillsInput.value.trim() : '';
    const skills = skillsRaw.split(',').map(s => s.trim()).filter(Boolean);

    if (!desiredRole) {
      roleInput && roleInput.focus();
      return;
    }

    // Loading state
    if (btn) btn.disabled = true;
    if (icon) icon.style.display = 'none';
    if (text) text.textContent = 'Analysing with AI…';
    if (spinner) spinner.style.display = 'inline-block';

    const sId = state.currentUser ? state.currentUser.student_id : 'STU-2026';
    const sName = state.currentUser ? state.currentUser.full_name : 'Student';

    const payload = {
      student_id: sId,
      student_name: sName,
      current_semester: currentSemester,
      desired_role: desiredRole,
      skills: skills,
      attendance: state.attendance || 94.0,
      study_hours: state.studyHours || 14.0,
    };

    try {
      const result = await window.api.groqAnalyze(payload);
      renderGroqAnalysisResult(result);
    } catch (err) {
      console.error('Groq AI analysis failed:', err);
      const panel = document.getElementById('groq-analysis-results');
      if (panel) {
        panel.style.display = 'block';
        panel.innerHTML = `
          <div style="background:#fef2f2;border:1px solid #fca5a5;border-radius:12px;padding:1rem;color:#991b1b;font-size:0.88rem;">
            <strong>⚠️ AI Analysis Error:</strong> ${err.message || 'Could not connect to Groq AI. Please try again.'}
          </div>
        `;
      }
    } finally {
      if (btn) btn.disabled = false;
      if (icon) { icon.style.display = 'inline'; icon.textContent = '🚀'; }
      if (text) text.textContent = 'Run AI Analysis';
      if (spinner) spinner.style.display = 'none';
    }
  }

  // Bind the "Run AI Analysis" button
  const btnGroq = document.getElementById('btn-run-groq-analysis');
  if (btnGroq) {
    btnGroq.addEventListener('click', runGroqAnalysis);
  }

  await initApp();

  // After app init, load aspirations for the active user
  if (state.currentUser) {
    await loadStudentAspirations(state.currentUser.student_id);
  }
});
