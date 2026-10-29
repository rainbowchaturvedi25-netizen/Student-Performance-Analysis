"""
Marks Calculation & Student Performance Analysis Engine.
Computes subject-wise grades, total percentages, GPA, Pass/Fail status,
predictive risk scoring, key performance drivers, and what-if sensitivity simulations.
"""

from typing import List, Tuple, Dict, Any
from .models import (
    StudentMarksEntry,
    StudentMarksReport,
    SubjectResult,
    StudentAnalysisInput,
    AnalysisResponse,
    SubjectBreakdownItem,
    ImpactDriverItem,
    WhatIfScenarioItem,
    MetricsSummary,
)


def get_subject_grade(marks: float) -> Tuple[str, str, str]:
    """Returns (letter_grade, pass_fail_status, remarks)."""
    if marks >= 90.0:
        return "A+", "PASS", "Outstanding mastery and concept comprehension"
    elif marks >= 80.0:
        return "A", "PASS", "Excellent understanding of curriculum"
    elif marks >= 70.0:
        return "B+", "PASS", "Very good analytical and problem-solving skills"
    elif marks >= 60.0:
        return "B", "PASS", "Good performance; consistent fundamentals"
    elif marks >= 50.0:
        return "C", "PASS", "Average performance; needs deeper revision"
    elif marks >= 40.0:
        return "D", "PASS", "Passing threshold met; requires extra practice"
    else:
        return "F", "FAIL", "Did not meet 40% passing benchmark; remedial required"


def compute_gpa(percentage: float) -> float:
    """Converts percentage to standard 4.0 GPA scale."""
    if percentage >= 90.0:
        return 4.0
    elif percentage >= 85.0:
        return 3.8
    elif percentage >= 80.0:
        return 3.6
    elif percentage >= 75.0:
        return 3.3
    elif percentage >= 70.0:
        return 3.0
    elif percentage >= 65.0:
        return 2.7
    elif percentage >= 60.0:
        return 2.4
    elif percentage >= 55.0:
        return 2.0
    elif percentage >= 50.0:
        return 1.7
    elif percentage >= 40.0:
        return 1.0
    else:
        return 0.0


def score_to_letter_grade(score: float) -> str:
    """Converts continuous composite score to letter grade."""
    if score >= 90.0:
        return "A+"
    elif score >= 80.0:
        return "A"
    elif score >= 70.0:
        return "B+"
    elif score >= 60.0:
        return "B"
    elif score >= 50.0:
        return "C"
    elif score >= 40.0:
        return "D"
    else:
        return "F"


def compute_composite_score(
    att: float,
    asg: float,
    exm: float,
    hrs: float,
    gpa: float,
    slp: float
) -> float:
    """
    Weighted predictive indicator formula:
    - Exam Performance: 35%
    - Coursework / Assignments: 25%
    - Attendance Rate: 20%
    - Study Routine: 10% (scaled, 16h/wk = 100%)
    - Prior Academic Baseline: 7% (4.0 GPA = 100%)
    - Sleep Hygiene: 3% (7.5h = 100%, penalties for severe deprivation or oversleeping)
    """
    study_norm = min(100.0, (hrs / 16.0) * 100.0)
    gpa_norm = min(100.0, (gpa / 4.0) * 100.0)
    
    # Sleep penalty curve: optimal between 7 and 9 hours
    if 7.0 <= slp <= 9.0:
        sleep_norm = 100.0
    elif slp < 7.0:
        sleep_norm = max(30.0, 100.0 - (7.0 - slp) * 20.0)
    else:
        sleep_norm = max(50.0, 100.0 - (slp - 9.0) * 15.0)

    raw_score = (
        exm * 0.35 +
        asg * 0.25 +
        att * 0.20 +
        study_norm * 0.10 +
        gpa_norm * 0.07 +
        sleep_norm * 0.03
    )
    return round(max(0.0, min(100.0, raw_score)), 1)


def classify_risk(predicted_score: float, att: float, asg: float, exm: float) -> Tuple[str, str, str]:
    """
    Returns (risk_level, risk_color, risk_badge)
    Risk levels:
    - High Achiever: #6366f1 (Indigo)
    - On Track: #10b981 (Emerald)
    - Moderate Risk: #f59e0b (Amber)
    - Critical Intervention: #ef4444 (Red)
    """
    if predicted_score >= 85.0 and att >= 85.0 and exm >= 75.0:
        return "High Achiever", "#6366f1", "High Achiever"
    elif predicted_score >= 70.0 and att >= 75.0 and exm >= 60.0:
        return "On Track", "#10b981", "On Track"
    elif predicted_score >= 55.0 or att >= 65.0:
        return "Moderate Risk", "#f59e0b", "Moderate Risk"
    else:
        return "Critical Intervention", "#ef4444", "Critical Intervention"


# ==============================================================================
# Marks Report Generation
# ==============================================================================

def calculate_marks_report(entry: StudentMarksEntry) -> StudentMarksReport:
    """
    Computes authentic official report card metrics, subject mastery,
    and diagnostic feedback from individual subject marks.
    """
    subjects_map = {
        "Mathematics": entry.marks.mathematics,
        "Science & Tech": entry.marks.science,
        "English Language": entry.marks.english,
        "Social Studies": entry.marks.social_studies,
        "Computer Science": entry.marks.computer_science,
    }

    subject_results: List[SubjectResult] = []
    total_obtained = 0.0
    failed_count = 0
    highest_subject = ""
    highest_score = -1.0
    lowest_subject = ""
    lowest_score = 999.0

    for sub_name, marks in subjects_map.items():
        total_obtained += marks
        grade, status, remarks = get_subject_grade(marks)
        
        if status == "FAIL":
            failed_count += 1

        if marks > highest_score:
            highest_score = marks
            highest_subject = sub_name

        if marks < lowest_score:
            lowest_score = marks
            lowest_subject = sub_name

        subject_results.append(
            SubjectResult(
                subject=sub_name,
                marks_obtained=marks,
                max_marks=100.0,
                percentage=marks,
                grade=grade,
                status=status,
                remarks=remarks
            )
        )

    # Aggregates
    max_total = 500.0
    percentage = round((total_obtained / max_total) * 100.0, 1)
    gpa = compute_gpa(percentage)
    overall_grade = score_to_letter_grade(percentage)

    # Final Result
    final_result = "FAILED" if failed_count > 0 else "PASSED"

    # Academic Standing Classification
    if final_result == "FAILED":
        academic_status = f"Remedial Required (Failed in {failed_count} Subject{'s' if failed_count > 1 else ''})"
    elif percentage >= 75.0:
        academic_status = "Distinction (≥75%)"
    elif percentage >= 60.0:
        academic_status = "First Class (≥60%)"
    elif percentage >= 50.0:
        academic_status = "Second Class (≥50%)"
    else:
        academic_status = "Pass Class (≥40%)"

    # Risk Tier
    att = entry.attendance
    hrs = entry.study_hours_weekly
    asg = entry.assignment_completion

    if final_result == "FAILED" or percentage < 45.0 or att < 65.0:
        risk_tier = "Critical Intervention"
        risk_color = "#ef4444"
    elif percentage < 65.0 or att < 75.0 or asg < 70.0:
        risk_tier = "Moderate Risk"
        risk_color = "#f59e0b"
    elif percentage < 85.0:
        risk_tier = "On Track"
        risk_color = "#10b981"
    else:
        risk_tier = "High Achiever"
        risk_color = "#6366f1"

    # Strengths
    strengths: List[str] = []
    if highest_score >= 80.0:
        strengths.append(f"Top-performing subject: {highest_subject} with an impressive score of {highest_score:.0f}/100 ({overall_grade}).")
    if att >= 90.0:
        strengths.append(f"Punctual and consistent classroom presence ({att:.1f}% attendance record).")
    if asg >= 85.0:
        strengths.append(f"High dedication to coursework and assignment deliverables ({asg:.0f}% completion).")
    if hrs >= 12.0:
        strengths.append(f"Rigorous independent study discipline ({hrs:.1f} hours/week).")
    if not strengths:
        strengths.append("Foundational knowledge established across core topics; primed for advancement.")

    # Growth Areas
    growth_areas: List[str] = []
    if failed_count > 0:
        growth_areas.append(f"Urgent focus needed in {failed_count} subject(s) scoring below the 40% passing benchmark.")
    if lowest_score < 60.0:
        growth_areas.append(f"Lowest subject score: {lowest_subject} ({lowest_score:.0f}/100) requires targeted remedial attention.")
    if att < 75.0:
        growth_areas.append(f"Attendance is {att:.1f}%, which falls below the mandatory 75% threshold.")
    if hrs < 6.0:
        growth_areas.append(f"Independent study time of {hrs:.1f} hrs/week is insufficient for advanced problem solving.")
    if asg < 70.0:
        growth_areas.append(f"Assignment completion rate ({asg:.0f}%) indicates missed practice assignments.")

    # Tailored Recommendations
    recommendations: List[str] = []
    if lowest_score < 50.0:
        recommendations.append(f"Schedule 2 weekly 1-on-1 tutoring sessions focusing specifically on {lowest_subject} core concepts.")
    if att < 80.0:
        recommendations.append("Establish an attendance commitment plan to ensure no instructional lectures are missed.")
    if hrs < 10.0:
        recommendations.append(f"Increase weekly study schedule from {hrs:.0f} hrs to 10-12 hrs using structured 45-minute study blocks.")
    if asg < 75.0:
        recommendations.append("Utilize guided homework clinic hours to ensure 100% on-time submission of future assignments.")
    if not recommendations:
        recommendations.append(f"Maintain the stellar academic performance; explore honors projects or Olympiad prep in {highest_subject}.")

    return StudentMarksReport(
        roll_no=entry.roll_no,
        name=entry.name,
        grade_class=entry.grade_class,
        term=entry.term,
        total_obtained=round(total_obtained, 1),
        max_total=max_total,
        percentage=percentage,
        overall_grade=overall_grade,
        gpa=gpa,
        final_result=final_result,
        failed_subject_count=failed_count,
        highest_subject=highest_subject,
        highest_score=highest_score,
        lowest_subject=lowest_subject,
        lowest_score=lowest_score,
        academic_status=academic_status,
        risk_tier=risk_tier,
        risk_color=risk_color,
        attributes={
            "attendance": att,
            "study_hours_weekly": hrs,
            "assignment_completion": asg,
            "sleep_hours": entry.sleep_hours,
            "extracurricular": entry.extracurricular,
        },
        subject_results=subject_results,
        strengths=strengths,
        growth_areas=growth_areas,
        recommendations=recommendations,
        teacher_remarks=entry.teacher_remarks or "Marks recorded in portal database.",
    )


# ==============================================================================
# Full AI Performance Analysis & Sensitivity Simulation
# ==============================================================================

def analyze_student_performance(student: StudentAnalysisInput) -> AnalysisResponse:
    """
    Primary Diagnostic & Marks Result Evaluation Endpoint:
    Accepts student indicators and subject marks (Mathematics, Science & Tech, English, Social Studies, CS).
    Calculates total marks obtained, percentage, letter grade, GPA, pass/fail status,
    academic standing (Distinction, First Class, Remedial), risk tier, subject breakdowns,
    key strengths/growth drivers, recommendations, and what-if sensitivity simulations.
    """
    att = student.attendance if student.attendance is not None else 90.0
    hrs = student.study_hours if student.study_hours is not None else 10.0
    gpa_in = student.previous_gpa if student.previous_gpa is not None else 3.2
    slp = student.sleep_hours if student.sleep_hours is not None else 7.5

    # 1. Subject marks evaluation
    if student.marks:
        math = student.marks.mathematics
        science = student.marks.science
        english = student.marks.english
        social = student.marks.social_studies
        cs = student.marks.computer_science

        exm = round((math + science + cs) / 3.0, 1)
        asg = round((english + social + cs) / 3.0, 1)
    else:
        exm = student.exam_score if student.exam_score is not None else 82.0
        asg = student.assignment_avg if student.assignment_avg is not None else 85.0
        math = round(max(0.0, min(100.0, exm * 0.95 + (hrs / 15.0) * 5.0)), 1)
        science = round(max(0.0, min(100.0, (exm + asg) / 2.0)), 1)
        english = round(max(0.0, min(100.0, asg * 0.92 + att * 0.08)), 1)
        social = round(max(0.0, min(100.0, (asg * 0.6 + exm * 0.4))), 1)
        cs = round(max(0.0, min(100.0, exm * 0.9 + (hrs / 12.0) * 10.0)), 1)

    subjects = [
        ("Mathematics", math),
        ("Science & Tech", science),
        ("English Language", english),
        ("Social Studies", social),
        ("Computer Science", cs),
    ]

    total_obtained = round(math + science + english + social + cs, 1)
    percentage = round((total_obtained / 500.0) * 100.0, 1)
    gpa = compute_gpa(percentage)

    subject_breakdowns: List[SubjectBreakdownItem] = []
    failed_count = 0
    highest_subject = ""
    highest_score = -1.0
    lowest_subject = ""
    lowest_score = 999.0

    for sub_name, score in subjects:
        g, status, rem = get_subject_grade(score)
        if status == "FAIL":
            failed_count += 1
        if score > highest_score:
            highest_score = score
            highest_subject = sub_name
        if score < lowest_score:
            lowest_score = score
            lowest_subject = sub_name

        subject_breakdowns.append(
            SubjectBreakdownItem(
                subject=sub_name,
                score=score,
                grade=g,
                status=status,
                remarks=rem
            )
        )

    # Final Result & Academic Standing
    final_result = "FAILED" if failed_count > 0 else "PASSED"

    if final_result == "FAILED":
        academic_status = f"Remedial Required (Failed in {failed_count} Subject{'s' if failed_count > 1 else ''})"
    elif percentage >= 75.0:
        academic_status = "Distinction (≥75%)"
    elif percentage >= 60.0:
        academic_status = "First Class (≥60%)"
    elif percentage >= 50.0:
        academic_status = "Second Class (≥50%)"
    else:
        academic_status = "Pass Class (≥40%)"

    # Predicted Score & Risk Level
    predicted_score = percentage
    letter_grade = score_to_letter_grade(predicted_score)
    risk_level, risk_color, _ = classify_risk(predicted_score, att, asg, exm)
    if final_result == "FAILED":
        risk_level = "Critical Intervention"
        risk_color = "#ef4444"

    confidence = round(max(89.0, min(98.5, 98.0 - (failed_count * 2.5))), 1)

    # Key Impact Drivers
    impact_drivers: List[ImpactDriverItem] = []

    if highest_score >= 80.0:
        impact_drivers.append(ImpactDriverItem(
            factor=f"Strong {highest_subject}",
            points=round((highest_score - 70.0) * 0.25, 1),
            impact="positive",
            description=f"Top mastery in {highest_subject} ({highest_score:.0f}/100) boosts overall academic standing."
        ))

    if lowest_score < 50.0:
        impact_drivers.append(ImpactDriverItem(
            factor=f"Deficit in {lowest_subject}",
            points=round((lowest_score - 60.0) * 0.3, 1),
            impact="negative",
            description=f"{lowest_subject} scored {lowest_score:.0f}/100, dragging down overall marks and result."
        ))

    if att >= 90.0:
        impact_drivers.append(ImpactDriverItem(
            factor="Consistent Attendance",
            points=+3.5,
            impact="positive",
            description=f"Strong attendance record of {att:.0f}% supports ongoing concept retention."
        ))
    elif att < 75.0:
        impact_drivers.append(ImpactDriverItem(
            factor="Attendance Deficit",
            points=-4.0,
            impact="warning",
            description=f"Attendance of {att:.0f}% is below mandatory institutional benchmarks."
        ))

    if hrs >= 12.0:
        impact_drivers.append(ImpactDriverItem(
            factor="Disciplined Study Routine",
            points=+3.0,
            impact="positive",
            description=f"{hrs:.1f} weekly study hours reinforces exam readiness."
        ))
    elif hrs < 6.0:
        impact_drivers.append(ImpactDriverItem(
            factor="Insufficient Revision Time",
            points=-3.0,
            impact="warning",
            description=f"Only {hrs:.1f} hrs/week self-study limits problem-solving practice."
        ))

    # Recommendations
    recommendations: List[str] = []
    if failed_count > 0:
        recommendations.append(f"Immediate remedial tutorials required in {lowest_subject} to achieve the 40% passing threshold.")
    if lowest_score < 60.0 and failed_count == 0:
        recommendations.append(f"Targeted revision in {lowest_subject} (current: {lowest_score:.0f}%) to elevate from passing to First Class.")
    if att < 80.0:
        recommendations.append(f"Improve lecture attendance from {att:.0f}% to ≥85% to ensure full syllabus coverage.")
    if hrs < 10.0:
        recommendations.append(f"Schedule 10-12 weekly self-study hours with focused revision on technical subjects.")
    if not recommendations:
        recommendations.append(f"Outstanding academic mastery across all 5 subjects. Primed for academic honors and distinction!")

    # What-If Sensitivity Scenarios
    what_if_scenarios: List[WhatIfScenarioItem] = []

    # Scenario 1: Boost lowest subject
    target_low = min(100.0, lowest_score + 15.0)
    s1_total = total_obtained - lowest_score + target_low
    s1_pct = round((s1_total / 500.0) * 100.0, 1)
    s1_delta = round(s1_pct - percentage, 1)
    what_if_scenarios.append(WhatIfScenarioItem(
        scenario=f"Remedial Boost: +15 Marks in {lowest_subject}",
        delta=s1_delta,
        predicted_score=s1_pct,
        projected_grade=score_to_letter_grade(s1_pct)
    ))

    # Scenario 2: +4 hrs study time
    s2_total = min(500.0, total_obtained + 18.0)
    s2_pct = round((s2_total / 500.0) * 100.0, 1)
    s2_delta = round(s2_pct - percentage, 1)
    what_if_scenarios.append(WhatIfScenarioItem(
        scenario="Study Habit Elevation (+4 hrs/wk study time)",
        delta=s2_delta,
        predicted_score=s2_pct,
        projected_grade=score_to_letter_grade(s2_pct)
    ))

    # Scenario 3: All subjects +8 marks
    s3_total = min(500.0, total_obtained + 40.0)
    s3_pct = round((s3_total / 500.0) * 100.0, 1)
    s3_delta = round(s3_pct - percentage, 1)
    what_if_scenarios.append(WhatIfScenarioItem(
        scenario="Uniform Improvement (+8 marks across all subjects)",
        delta=s3_delta,
        predicted_score=s3_pct,
        projected_grade=score_to_letter_grade(s3_pct)
    ))

    return AnalysisResponse(
        student_name=student.name,
        student_id=student.student_id,
        grade_class=student.grade_class or "Grade 10-A",
        term=student.term or "Midterm Examination",
        total_obtained=total_obtained,
        max_total=500.0,
        percentage=percentage,
        gpa=gpa,
        final_result=final_result,
        failed_subject_count=failed_count,
        academic_status=academic_status,
        highest_subject=highest_subject,
        highest_score=highest_score,
        lowest_subject=lowest_subject,
        lowest_score=lowest_score,
        predicted_score=predicted_score,
        letter_grade=letter_grade,
        risk_level=risk_level,
        risk_color=risk_color,
        confidence=confidence,
        metrics_summary=MetricsSummary(
            attendance=att,
            exam_score=exm,
            assignment_avg=asg,
            study_hours=hrs,
            sleep_hours=slp
        ),
        subject_breakdowns=subject_breakdowns,
        impact_drivers=impact_drivers,
        recommendations=recommendations,
        what_if_scenarios=what_if_scenarios
    )


# ==============================================================================
# Semester SGPA, CGPA & Placement Evaluation Engine (10-Point Scale)
# ==============================================================================

def marks_to_grade_point(marks: float) -> Tuple[int, str, str, bool]:
    """
    Standard University 10-Point Absolute Grading System (UGC / AICTE):
    - 90 - 100: Grade Point 10 (O - Outstanding)
    - 80 - 89.9: Grade Point 9  (A+ - Excellent)
    - 70 - 79.9: Grade Point 8  (A - Very Good)
    - 60 - 69.9: Grade Point 7  (B+ - Good)
    - 50 - 59.9: Grade Point 6  (B - Above Average)
    - 45 - 49.9: Grade Point 5  (C - Average)
    - 40 - 44.9: Grade Point 4  (P - Pass Threshold)
    - < 40     : Grade Point 0  (F - Fail / Arrear / Backlog)
    Returns: (grade_point, grade_letter, remarks, passed)
    """
    m = round(float(marks), 1)
    if m >= 90.0:
        return 10, "O", "Outstanding concept mastery", True
    elif m >= 80.0:
        return 9, "A+", "Excellent performance", True
    elif m >= 70.0:
        return 8, "A", "Very good analytical understanding", True
    elif m >= 60.0:
        return 7, "B+", "Good solid fundamentals", True
    elif m >= 50.0:
        return 6, "B", "Above average; consistent practice needed", True
    elif m >= 45.0:
        return 5, "C", "Average; remedial review advised", True
    elif m >= 40.0:
        return 4, "P", "Pass threshold met", True
    else:
        return 0, "F", "Backlog (Below 40 passing benchmark)", False


def compute_semester_sgpa(subjects: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculates Semester Grade Point Average (SGPA):
    SGPA = Sum(Credits * Grade_Points) / Sum(Credits)
    Also computes total marks, percentage, and counts active backlogs.
    """
    total_credit_points = 0.0
    total_credits = 0.0
    total_obtained = 0.0
    max_total = 0.0
    backlogs = 0
    enriched_subjects = []

    for s in subjects:
        marks = float(s.get("marks", 0.0))
        credits = float(s.get("credits", 4.0))
        gp, letter, remarks, passed = marks_to_grade_point(marks)

        if not passed:
            backlogs += 1

        total_credit_points += (credits * gp)
        total_credits += credits
        total_obtained += marks
        max_total += 100.0

        enriched_subjects.append({
            "code": s.get("code", "SUB"),
            "name": s.get("name", "Subject"),
            "credits": credits,
            "marks": marks,
            "grade_point": gp,
            "grade_letter": letter,
            "passed": passed,
            "remarks": remarks
        })

    sgpa = round(total_credit_points / max(1.0, total_credits), 2)
    percentage = round((total_obtained / max(1.0, max_total)) * 100.0, 1)

    return {
        "sgpa": sgpa,
        "percentage": percentage,
        "total_obtained": total_obtained,
        "max_total": max_total,
        "total_credits": total_credits,
        "backlogs_count": backlogs,
        "status": "BACKLOG" if backlogs > 0 else "PASSED",
        "subjects": enriched_subjects
    }


def evaluate_placement_eligibility(
    avg_cgpa: float,
    total_backlogs: int,
    total_credits_earned: float,
    semester_count: int = 8
) -> Dict[str, Any]:
    """
    Evaluates campus placement eligibility with visual traffic light classification:
    - GREEN LIGHT (YES · ELIGIBLE FOR PLACEMENT):
        Average CGPA >= 7.0 and 0 active backlogs. Cleared for all major hiring drives.
    - YELLOW LIGHT (CAUTION · CONDITIONAL / BORDERLINE):
        Average CGPA between 6.0 and 6.99 (with 0 backlogs), or CGPA >= 7.0 with 1 active backlog.
        Eligible for select mass recruiters / tier-2 companies, caution advised.
    - RED LIGHT (NO · NOT ELIGIBLE FOR PLACEMENTS):
        Average CGPA < 6.0 or active backlogs > 1 (or any backlogs if CGPA < 7.0).
        Fails standard campus placement threshold.
    """
    reasons = []
    action_plan = []
    avg = round(float(avg_cgpa), 2)

    # 1. Check Backlog condition
    if total_backlogs == 0:
        if avg >= 7.5:
            light_color = "GREEN"
            light_class = "green"
            status = "ELIGIBLE"
            light_label = "YES · ELIGIBLE FOR PLACEMENT"
            tier1 = avg >= 8.0
            tier2 = True
            tier3 = True
            readiness = min(100.0, round(avg * 10.5, 1))
            headline = "Candidate Cleared for Campus Placements with Honors"
            summary = (
                f"Student maintains an exemplary academic profile with an Average CGPA of {avg}/10.0 "
                f"and 0 active backlogs across all {semester_count} semesters. Fully eligible for Tier-1 Product Companies, "
                f"Core Engineering R&D, and Global IT Tech roles."
            )
            reasons.append(f"Cumulative CGPA of {avg}/10.0 exceeds institutional placement benchmarks (>= 7.0).")
            reasons.append("Zero active backlogs across all semesters.")
            reasons.append("Eligible for premium Day-1 & Day-2 Dream placement slots.")
            action_plan.append("Prepare System Design, Data Structures & Algorithms, and LeetCode Medium/Hard for Tier-1 interviews.")
            action_plan.append("Refine technical resume highlighting capstone projects and internship experience.")
            action_plan.append("Participate in competitive coding hackathons to target 15+ LPA dream offers.")

        elif avg >= 7.0:
            light_color = "GREEN"
            light_class = "green"
            status = "ELIGIBLE"
            light_label = "YES · ELIGIBLE FOR PLACEMENT"
            tier1 = False
            tier2 = True
            tier3 = True
            readiness = round(avg * 10.2, 1)
            headline = "Candidate Cleared for Campus Placements"
            summary = (
                f"Student holds a solid Average CGPA of {avg}/10.0 with 0 backlogs. "
                f"Eligible for Core Engineering and IT Consulting firms. Target >= 8.0 for Tier-1 Dream Tech firms."
            )
            reasons.append(f"Cumulative CGPA of {avg}/10.0 satisfies campus placement baseline.")
            reasons.append("Clean academic sheet with 0 standing arrears.")
            action_plan.append("Focus on core technical aptitude and mock interviews.")
            action_plan.append("Maintain performance to keep CGPA comfortably above 7.0 cutoff.")

        elif avg >= 6.0:
            light_color = "YELLOW"
            light_class = "yellow"
            status = "CAUTION"
            light_label = "CAUTION · CONDITIONAL ELIGIBILITY"
            tier1 = False
            tier2 = avg >= 6.5
            tier3 = True
            readiness = round(avg * 9.8, 1)
            headline = "Conditional Eligibility · Caution Required"
            summary = (
                f"Student is in the cautionary / borderline placement zone with an Average CGPA of {avg}/10.0. "
                f"While eligible for Mass Recruiters (TCS, Infosys, Wipro, Cognizant, Accenture) whose cutoff is 6.0, "
                f"the candidate is currently filtered out of Tier-1 and Core Technical companies (cutoff 7.0 - 8.0)."
            )
            reasons.append(f"CGPA of {avg}/10.0 meets minimum mass recruiter threshold (>= 6.0) but falls short of Tier-1 (>= 7.5).")
            reasons.append("Borderline academic margin; any dropped subject may push student into ineligibility.")
            action_plan.append("Target at least 8.0+ SGPA in remaining evaluations to elevate overall CGPA above 7.0.")
            action_plan.append("Focus heavily on aptitude, reasoning, and standard verbal/coding assessments for mass drives.")
            action_plan.append("Earn industry credentials (AWS, Cloud, Full-Stack) to compensate for moderate CGPA.")

        else:
            light_color = "RED"
            light_class = "red"
            status = "INELIGIBLE"
            light_label = "NO · NOT ELIGIBLE FOR PLACEMENTS"
            tier1 = False
            tier2 = False
            tier3 = False
            readiness = max(20.0, round(avg * 7.5, 1))
            headline = "Not Eligible for Campus Placements"
            summary = (
                f"Average CGPA of {avg}/10.0 is below the universal minimum eligibility threshold of 6.0 CGPA "
                f"required by campus recruitment policies."
            )
            reasons.append(f"Average CGPA ({avg}/10.0) is below the minimum company cutoff of 6.00.")
            action_plan.append("Request grade improvement exams to raise course marks.")
            action_plan.append("Focus on scoring 8.5+ SGPA in next semesters to pull up cumulative CGPA.")

    else:
        # Active backlogs present
        if total_backlogs == 1 and avg >= 7.0:
            light_color = "YELLOW"
            light_class = "yellow"
            status = "CAUTION"
            light_label = "CAUTION · 1 ACTIVE BACKLOG DETECTED"
            tier1 = False
            tier2 = False
            tier3 = True
            readiness = 55.0
            headline = "Conditional Eligibility · Backlog Remedial Needed"
            summary = (
                f"Student holds a good CGPA of {avg}/10.0, but has 1 active backlog. "
                f"Most companies require 0 active backlogs at the time of joining. Immediate supplementary exam clearance needed."
            )
            reasons.append("1 active backlog requires clearance prior to official offer letter onboarding.")
            reasons.append("Select mass recruiters permit registration if backlog is cleared before final graduation.")
            action_plan.append("Register immediately for supplementary exam to clear the pending subject.")
            action_plan.append("Dedicate 2 hours daily to revision of the backlog subject fundamentals.")
        else:
            light_color = "RED"
            light_class = "red"
            status = "INELIGIBLE"
            light_label = "NO · NOT ELIGIBLE FOR PLACEMENTS"
            tier1 = False
            tier2 = False
            tier3 = False
            readiness = max(15.0, round(avg * 6.0, 1))
            headline = "Ineligible · Multiple Active Backlogs"
            summary = (
                f"Candidate currently has {total_backlogs} active backlog(s) and an Average CGPA of {avg}/10.0. "
                f"Campus placement policies strictly disqualify candidates with standing arrears."
            )
            reasons.append(f"{total_backlogs} active backlogs violate standard 0-backlog campus recruitment criteria.")
            if avg < 6.0:
                reasons.append(f"Average CGPA of {avg}/10.0 is also below the 6.0 minimum requirement.")
            action_plan.append("Mandatory clearance of all active backlogs in upcoming supplementary examination cycles.")
            action_plan.append("Meet academic counselor to establish structured remedial study timetable.")

    return {
        "eligible": (light_color == "GREEN"),
        "status": status,
        "light_color": light_color,
        "light_label": light_label,
        "light_class": light_class,
        "avg_cgpa": avg,
        "total_backlogs": total_backlogs,
        "total_credits_earned": total_credits_earned,
        "total_credits_required": 160.0,
        "tier1_eligible": tier1,
        "tier2_eligible": tier2,
        "tier3_eligible": tier3,
        "readiness_score": readiness,
        "headline": headline,
        "summary": summary,
        "reasons": reasons,
        "action_plan": action_plan
    }


