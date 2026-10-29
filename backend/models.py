"""
Data models and schemas for Student Performance Analysis & Marks Portal.
Provides validation schemas for predictive diagnostics, cohort analytics, and marksheet generation.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# ==============================================================================
# 1. Subject Marks & Official Report Card Schemas
# ==============================================================================

class SubjectMarks(BaseModel):
    mathematics: float = Field(..., ge=0.0, le=100.0, description="Marks obtained in Mathematics (0-100)")
    science: float = Field(..., ge=0.0, le=100.0, description="Marks obtained in Science & Tech (0-100)")
    english: float = Field(..., ge=0.0, le=100.0, description="Marks obtained in English Language (0-100)")
    social_studies: float = Field(..., ge=0.0, le=100.0, description="Marks obtained in Social Studies (0-100)")
    computer_science: float = Field(..., ge=0.0, le=100.0, description="Marks obtained in Computer Science (0-100)")


class StudentMarksEntry(BaseModel):
    name: str = Field(..., min_length=1, description="Student's Full Name")
    roll_no: str = Field(..., min_length=1, description="Roll Number or Identifier (e.g., STU-2026)")
    grade_class: str = Field("Grade 10-A", description="Class / Section / Semester")
    term: str = Field("Midterm Examination", description="Academic term or exam cycle")
    
    # Subject-wise marks
    marks: SubjectMarks
    
    # Learning & behavioral attributes
    attendance: float = Field(..., ge=0.0, le=100.0, description="Class attendance percentage (0-100)")
    study_hours_weekly: float = Field(..., ge=0.0, le=60.0, description="Weekly independent self-study hours (0-60)")
    assignment_completion: float = Field(..., ge=0.0, le=100.0, description="Assignment submission percentage (0-100)")
    sleep_hours: float = Field(7.5, ge=3.0, le=12.0, description="Average sleep per night (hours)")
    extracurricular: str = Field("Moderate", description="Extracurricular participation: High, Moderate, Low")
    teacher_remarks: Optional[str] = Field("", description="Optional educator notes or behavioral feedback")


class SubjectResult(BaseModel):
    subject: str
    marks_obtained: float
    max_marks: float = 100.0
    percentage: float
    grade: str
    status: str  # "PASS" or "FAIL"
    remarks: str


class StudentMarksReport(BaseModel):
    roll_no: str
    name: str
    grade_class: str
    term: str
    
    # Overall Marks
    total_obtained: float
    max_total: float = 500.0
    percentage: float
    overall_grade: str
    gpa: float
    final_result: str  # "PASSED" or "FAILED"
    failed_subject_count: int
    
    # Key Highlights
    highest_subject: str
    highest_score: float
    lowest_subject: str
    lowest_score: float
    academic_status: str
    risk_tier: str
    risk_color: str
    
    # Attributes & Context
    attributes: Dict[str, Any]
    
    # Subject breakdowns
    subject_results: List[SubjectResult]
    
    # Insights & Recommendations
    strengths: List[str]
    growth_areas: List[str]
    recommendations: List[str]
    teacher_remarks: str


class ClassMarksSummary(BaseModel):
    total_students: int
    class_average_percentage: float
    highest_percentage: float
    lowest_percentage: float
    pass_percentage: float
    total_passed: int
    total_failed: int
    subject_class_averages: Dict[str, float]
    grade_distribution: Dict[str, int]
    risk_distribution: Dict[str, int]
    students_list: List[Dict[str, Any]]


# ==============================================================================
# 2. Predictive Performance Analysis & Simulation Schemas
# ==============================================================================

class StudentAnalysisInput(BaseModel):
    name: str = Field("Student Profile", min_length=1, description="Student's Full Name")
    student_id: str = Field("STU-2026", min_length=1, description="Student Roll No / ID (e.g. STU-2026)")
    grade_class: Optional[str] = Field("Grade 10-A", description="Class / Section / Semester")
    term: Optional[str] = Field("Midterm Examination", description="Academic term or exam cycle")
    marks: Optional[SubjectMarks] = Field(None, description="Direct subject-wise marks (Mathematics, Science, English, Social, CS)")
    attendance: Optional[float] = Field(92.0, ge=0.0, le=100.0, description="Attendance percentage (0-100)")
    assignment_avg: Optional[float] = Field(88.0, ge=0.0, le=100.0, description="Coursework / Assignment average (0-100)")
    exam_score: Optional[float] = Field(85.0, ge=0.0, le=100.0, description="Midterm or recent exam score (0-100)")
    study_hours: Optional[float] = Field(12.0, ge=0.0, le=50.0, description="Weekly independent self-study hours")
    previous_gpa: Optional[float] = Field(3.6, ge=0.0, le=4.0, description="Prior cumulative GPA (0.0-4.0)")
    sleep_hours: Optional[float] = Field(7.5, ge=3.0, le=12.0, description="Average nightly sleep (hours)")
    extracurricular: Optional[str] = Field("Moderate", description="Extracurricular involvement level")


class SubjectBreakdownItem(BaseModel):
    subject: str
    score: float
    grade: str
    status: str  # "PASS" or "FAIL"
    remarks: Optional[str] = ""


class ImpactDriverItem(BaseModel):
    factor: str
    points: float
    impact: str  # "positive", "negative", "warning"
    description: str


class WhatIfScenarioItem(BaseModel):
    scenario: str
    delta: float
    predicted_score: float
    projected_grade: str


class MetricsSummary(BaseModel):
    attendance: float
    exam_score: float
    assignment_avg: float
    study_hours: float
    sleep_hours: float


class AnalysisResponse(BaseModel):
    student_name: str
    student_id: str
    grade_class: str = "Grade 10-A"
    term: str = "Midterm Examination"
    
    # Official Marks Result Highlights
    total_obtained: float
    max_total: float = 500.0
    percentage: float
    gpa: float
    final_result: str  # "PASSED" or "FAILED"
    failed_subject_count: int = 0
    academic_status: str  # e.g. "Distinction (≥75%)", "First Class (≥60%)", "Second Class (≥50%)", "Remedial Required"
    highest_subject: str = ""
    highest_score: float = 0.0
    lowest_subject: str = ""
    lowest_score: float = 0.0

    # Predictive Performance & Risk Diagnostics
    predicted_score: float
    letter_grade: str
    risk_level: str
    risk_color: str
    confidence: float
    metrics_summary: MetricsSummary
    subject_breakdowns: List[SubjectBreakdownItem]
    impact_drivers: List[ImpactDriverItem]
    recommendations: List[str]
    what_if_scenarios: List[WhatIfScenarioItem]



# ==============================================================================
# 3. Cohort Analytics & Student Roster Schemas
# ==============================================================================

class CorrelationScatterPoint(BaseModel):
    x: float  # study_hours
    y: float  # exam_score
    name: str
    score: float  # predicted_score
    risk: str  # risk_level


class CohortSummary(BaseModel):
    cohort_average_score: float
    pass_rate: float
    at_risk_count: int
    total_students: int
    risk_distribution: Dict[str, int]
    correlation_scatter: List[CorrelationScatterPoint]
    subject_averages: Dict[str, float]


class StudentListItem(BaseModel):
    id: str
    name: str
    grade_level: str
    attendance: float
    assignment_avg: float
    exam_score: float
    study_hours: float
    previous_gpa: float
    sleep_hours: float
    predicted_score: float
    letter_grade: str
    risk_level: str
    risk_badge: str


class NewStudentInput(BaseModel):
    name: str = Field(..., min_length=1)
    attendance: float = Field(..., ge=0.0, le=100.0)
    assignment_avg: float = Field(..., ge=0.0, le=100.0)
    exam_score: float = Field(..., ge=0.0, le=100.0)
    study_hours: float = Field(..., ge=0.0, le=50.0)
    previous_gpa: float = Field(3.0, ge=0.0, le=4.0)
    sleep_hours: float = Field(7.0, ge=3.0, le=12.0)


# ==============================================================================
# 4. Single Student Personal Growth Schemas
# ==============================================================================

class TermGrowthPoint(BaseModel):
    term_id: str
    term_name: str
    date_label: str
    total_obtained: float
    percentage: float
    gpa: float
    grade: str
    final_result: str
    marks: Dict[str, float]
    attendance: float
    study_hours: float
    remarks: Optional[str] = ""


class SubjectGrowthDetail(BaseModel):
    subject: str
    baseline_score: float
    current_score: float
    growth_delta: float
    growth_percentage: float


class StudentPersonalGrowthProfile(BaseModel):
    student_id: str
    student_name: str
    grade_class: str
    academic_year: str
    current_term: str
    current_percentage: float
    current_gpa: float
    overall_grade: str
    final_result: str
    academic_status: str
    overall_growth_delta: float
    highest_growth_subject: str
    lowest_growth_subject: str
    target_score: float
    timeline: List[TermGrowthPoint]
    subject_growth: List[SubjectGrowthDetail]
    milestones: List[Dict[str, str]]
    growth_recommendations: List[str]


# ==============================================================================
# 5. All-Semester Evaluation & Placement Eligibility Schemas
# ==============================================================================

class SemesterSubjectDetail(BaseModel):
    code: str
    name: str
    credits: float = 4.0
    marks: float = Field(..., ge=0.0, le=100.0)
    grade_point: int = 10
    grade_letter: str = "O"
    passed: bool = True
    remarks: str = ""


class SemesterDetail(BaseModel):
    semester_num: int
    semester_id: str
    semester_name: str
    credits_total: float
    credits_earned: float
    total_marks: float
    max_marks: float
    percentage: float
    sgpa: float  # Individual Semester Grade Point Average (0.0 - 10.0 scale)
    backlogs_count: int
    status: str  # "PASSED" or "BACKLOG"
    subjects: List[SemesterSubjectDetail]


class PlacementEligibilityResult(BaseModel):
    eligible: bool
    status: str  # "ELIGIBLE", "CAUTION", "INELIGIBLE"
    light_color: str  # "GREEN", "YELLOW", "RED"
    light_label: str  # "YES · ELIGIBLE FOR PLACEMENTS", "CAUTION · CONDITIONAL", "NO · NOT ELIGIBLE"
    light_class: str  # "green", "yellow", "red"
    avg_cgpa: float  # Cumulative CGPA across all semesters (0.0 - 10.0 scale)
    total_backlogs: int
    total_credits_earned: float
    total_credits_required: float = 160.0
    tier1_eligible: bool  # Dream / Product Companies (>= 8.0 CGPA, 0 backlogs)
    tier2_eligible: bool  # Core Engineering (>= 7.0 CGPA, 0 backlogs)
    tier3_eligible: bool  # Mass Recruiters / IT Services (>= 6.0 CGPA, 0 backlogs)
    readiness_score: float  # 0 to 100%
    headline: str
    summary: str
    reasons: List[str]
    action_plan: List[str]


class StudentAllSemestersResponse(BaseModel):
    student_id: str
    student_name: str
    program: str = "B.Tech Computer Science & Engineering"
    batch: str = "2022 - 2026"
    total_semesters: int = 8
    active_semester: int = 8
    semesters: List[SemesterDetail]
    avg_cgpa: float  # Cumulative Average CGPA across all semesters (0.0 - 10.0)
    highest_sgpa: float
    lowest_sgpa: float
    total_credits: float
    total_backlogs: int
    placement: PlacementEligibilityResult


class UpdateSemesterMarksRequest(BaseModel):
    student_id: Optional[str] = Field("STU-2026", description="Student ID or Roll No")
    semester_num: int = Field(..., ge=1, le=8)
    marks: Dict[str, float]  # subject_code -> marks (0-100)


# ==============================================================================
# 6. Authentication & User Profile Schemas
# ==============================================================================

class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, description="Username or Roll Number")
    password: str = Field(..., min_length=1, description="Account Password")
    current_semester: Optional[int] = Field(None, ge=1, le=8, description="Student's current enrolled semester (1-8). Updates saved profile if provided.")


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=2, description="Desired login username")
    password: str = Field(..., min_length=4, description="Account password")
    full_name: str = Field(..., min_length=2, description="Student's Full Legal Name")
    student_id: str = Field(..., min_length=2, description="Student Roll Number / Enrollment ID")
    program: Optional[str] = Field("B.Tech Computer Science & Engineering", description="Degree Program")
    batch: Optional[str] = Field("2022 - 2026", description="Academic Batch Years")
    current_semester: Optional[int] = Field(5, ge=1, le=8, description="Student's current enrolled semester (1-8).")


class AuthResponse(BaseModel):
    token: str
    username: str
    full_name: str
    student_id: str
    program: str
    batch: str
    role: str = "student"
    current_semester: int = 5


# ==============================================================================
# 7. Groq AI Inference & Role Placement Schemas (openai/gpt-oss-120b)
# ==============================================================================

class GroqAnalysisRequest(BaseModel):
    student_id: Optional[str] = Field("STU-2026", description="Student Roll No / Identifier")
    student_name: Optional[str] = Field("Aarav Sharma", description="Student Name")
    current_semester: int = Field(6, ge=1, le=8, description="Current semester the student is enrolled in (1 to 8)")
    desired_role: str = Field("Full Stack Developer", min_length=2, description="Target career role")
    skills: List[str] = Field(
        default_factory=lambda: ["Python", "C++", "React", "SQL", "DSA"],
        description="List of student's current technical and professional skills"
    )
    attendance: Optional[float] = Field(94.0, ge=0.0, le=100.0)
    study_hours: Optional[float] = Field(14.0, ge=0.0, le=60.0)


class GroqAnalysisResponse(BaseModel):
    model_used: str = "openai/gpt-oss-120b"
    provider: str = "Groq AI (openai/gpt-oss-120b)"
    student_id: str
    student_name: str
    current_semester: int
    desired_role: str
    skills: List[str]
    confidence_score: float
    on_track_status: str  # "ON TRACK", "NEEDS ATTENTION", "AT RISK"
    on_track_explanation: str
    role_fit_verdict: str
    skill_match_percentage: float
    matching_skills: List[str]
    missing_critical_skills: List[str]
    semester_roadmap: List[str]
    interview_readiness: str
    placement_verdict: str  # "ELIGIBLE", "CAUTION", "INELIGIBLE"
    light_color: str  # "GREEN", "YELLOW", "RED"



