"""
FastAPI application for Student Performance Analysis & Marks Portal System.
Serves RESTful endpoints for predictive AI analysis, cohort intelligence,
student roster operations, and marksheet report card generation.
"""

from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .models import (
    StudentAnalysisInput,
    AnalysisResponse,
    CohortSummary,
    StudentListItem,
    NewStudentInput,
    StudentMarksEntry,
    StudentMarksReport,
    ClassMarksSummary,
    StudentPersonalGrowthProfile,
    StudentAllSemestersResponse,
    UpdateSemesterMarksRequest,
    PlacementEligibilityResult,
    LoginRequest,
    RegisterRequest,
    AuthResponse,
    GroqAnalysisRequest,
    GroqAnalysisResponse,
)
from .engine import analyze_student_performance, evaluate_placement_eligibility
from .data import marks_db
from .database import db
from .groq_analyzer import analyze_with_groq_model

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI(
    title="EduMetrics AI · Student Performance Analysis & Marks Portal API",
    description="Full-featured RESTful API providing real-time AI performance inference, what-if simulations, cohort intelligence, and authentic student marksheet generation.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for frontend and external callers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==============================================================================
# System Health & Diagnostic Endpoints
# ==============================================================================

@app.get("/api/health", tags=["System Diagnostics"])
def health_check():
    """System diagnostic health check."""
    return {
        "status": "online",
        "service": "EduMetrics AI & Marks Portal Engine",
        "version": "2.0.0",
        "total_semesters": len(marks_db.semesters),
        "student_name": marks_db.student_name,
    }


# ==============================================================================
# Authentication & User Management Endpoints (Local Database)
# ==============================================================================

@app.post("/api/auth/register", response_model=AuthResponse, tags=["Authentication"])
def register_student(payload: RegisterRequest):
    """
    Registers a new student profile in the local SQLite database.
    Creates an authentic 8-semester curriculum template for the student to enter marks.
    """
    try:
        user = db.register_user(
            username=payload.username,
            password=payload.password,
            full_name=payload.full_name,
            student_id=payload.student_id,
            program=payload.program or "B.Tech Computer Science & Engineering",
            batch=payload.batch or "2022 - 2026",
            current_semester=payload.current_semester or 5,
        )
        return AuthResponse(**user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@app.post("/api/auth/login", response_model=AuthResponse, tags=["Authentication"])
def login_student(payload: LoginRequest):
    """
    Authenticates student against local SQLite database.
    Permits login with username OR student roll number.
    Optionally updates the student's current_semester if provided.
    """
    user = db.authenticate_user(payload.username, payload.password, payload.current_semester)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username/roll number or password. Please try again."
        )
    return AuthResponse(**user)


@app.get("/api/auth/me", response_model=AuthResponse, tags=["Authentication"])
def get_current_user(token: Optional[str] = Query(None)):
    """Verifies active session token from local SQLite database."""
    if not token:
        user = db.get_user_by_id("STU-2026")
        if user:
            return AuthResponse(token="demo-preview-token", **user)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not logged in.")

    user = db.get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired or invalid.")
    return AuthResponse(token=token, **user)


# ==============================================================================
# All-Semesters Evaluation & Placement Eligibility Endpoints (Local Database)
# ==============================================================================

@app.get("/api/student/semesters", response_model=StudentAllSemestersResponse, tags=["Semester & Placement Engine"])
def get_all_semesters_evaluation(student_id: Optional[str] = Query(None)):
    """
    Evaluates student marks across all 8 semesters from local SQLite database:
    - Calculates individual semester SGPA for each semester (1 to 8)
    - Computes Cumulative / Average CGPA across all semesters
    - Determines campus placement eligibility with traffic light verdict:
        * GREEN LIGHT: Yes · Eligible for Placement (CGPA >= 7.0, 0 Backlogs)
        * YELLOW LIGHT: Caution · Conditional Eligibility (CGPA 6.0-6.99, or 1 Backlog)
        * RED LIGHT: No · Not Eligible for Placements (CGPA < 6.0 or multiple Backlogs)
    """
    target_id = student_id or "STU-2026"
    return db.get_student_all_semesters(target_id)


@app.post("/api/student/semesters/update", response_model=StudentAllSemestersResponse, tags=["Semester & Placement Engine"])
def update_semester_marks(payload: UpdateSemesterMarksRequest):
    """
    Updates subject marks for a specific semester in local SQLite database and immediately recalculates:
    - That semester's SGPA
    - Overall Cumulative Average CGPA of all semesters
    - Instant Placement Light status (Green / Yellow / Red)
    """
    try:
        target_id = payload.student_id or "STU-2026"
        return db.update_semester_marks(target_id, payload.semester_num, payload.marks)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update semester marks: {str(e)}"
        )


@app.post("/api/student/semesters/preset/{preset_name}", response_model=StudentAllSemestersResponse, tags=["Semester & Placement Engine"])
def load_semester_preset(preset_name: str, student_id: Optional[str] = Query(None)):
    """
    Loads one-click test benchmarks into SQLite database:
    - 'green' (or 'eligible'): Honors Distinction, CGPA ~9.75, 0 backlogs -> Green Light (YES)
    - 'yellow' (or 'caution'): Borderline, CGPA ~6.40, 0 backlogs -> Yellow Light (CAUTION)
    - 'red' (or 'at_risk'): Active Backlogs, CGPA ~5.55 -> Red Light (NO)
    - 'reset': Restores default academic transcript
    """
    try:
        target_id = student_id or "STU-2026"
        return db.apply_preset(target_id, preset_name)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to load preset: {str(e)}"
        )



@app.post("/api/placement/evaluate", response_model=PlacementEligibilityResult, tags=["Semester & Placement Engine"])
def evaluate_custom_placement(payload: Dict[str, Any]):
    """Calculates placement eligibility light for arbitrary CGPA and backlog counts."""
    try:
        cgpa = float(payload.get("avg_cgpa", 7.5))
        backlogs = int(payload.get("total_backlogs", 0))
        credits_earned = float(payload.get("total_credits_earned", 160.0))
        sem_count = int(payload.get("semester_count", 8))
        res = evaluate_placement_eligibility(cgpa, backlogs, credits_earned, sem_count)
        return PlacementEligibilityResult(**res)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to evaluate placement criteria: {str(e)}"
        )


# ==============================================================================
# Groq AI Placement & Role Fitment Analysis (openai/gpt-oss-120b)
# ==============================================================================

@app.post("/api/groq/analyze", response_model=GroqAnalysisResponse, tags=["Groq AI Placement Engine"])
def analyze_student_groq(req: GroqAnalysisRequest):
    """
    Evaluates student profile via Groq's openai/gpt-oss-120b model:
    - Analyzes student pacing based on Current Semester (1 to 8) to determine if they are on-track.
    - Evaluates fit for Desired Target Role (e.g. Full Stack Developer, Data Scientist, etc.).
    - Evaluates Student Skills, identifying strengths and missing critical skills.
    - Computes AI Placement Confidence Score (0-100%).
    - Generates tailored semester milestone roadmap and interview preparation advice.
    """
    try:
        s_id = req.student_id or "STU-2026"
        # Persist student aspirations in SQLite DB
        db.update_student_aspirations(s_id, req.current_semester, req.desired_role, req.skills)

        # Retrieve full academic history from SQLite database
        sem_data = db.get_student_all_semesters(s_id)
        sem_summary = [
            {"semester": s.semester_name, "sgpa": s.sgpa, "status": s.status, "backlogs": s.backlogs_count}
            for s in sem_data.semesters[:req.current_semester]
        ]

        profile_payload = {
            "student_name": sem_data.student_name,
            "student_id": sem_data.student_id,
            "program": sem_data.program,
            "current_semester": req.current_semester,
            "desired_role": req.desired_role,
            "skills": req.skills,
            "cgpa": sem_data.avg_cgpa,
            "backlogs": sem_data.total_backlogs,
            "semesters_summary": sem_summary,
            "attendance": req.attendance or 94.0,
            "study_hours": req.study_hours or 14.0,
        }

        analysis = analyze_with_groq_model(profile_payload)
        return GroqAnalysisResponse(**analysis)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Groq AI analysis failed: {str(e)}"
        )


@app.get("/api/student/aspirations", tags=["Groq AI Placement Engine"])
def get_student_aspirations(student_id: Optional[str] = Query(None)):
    """Retrieves student's saved current semester, desired role, and skills from SQLite."""
    s_id = student_id or "STU-2026"
    return db.get_student_aspirations(s_id)


# ==============================================================================
# Student Performance & Predictive AI Endpoints
# ==============================================================================

@app.post("/api/analyze", response_model=AnalysisResponse, tags=["Predictive Analysis"])
def analyze_student(student: StudentAnalysisInput):
    """
    Evaluates learning attributes (attendance, assignments, exam score, study hours, GPA, sleep)
    and returns a composite performance score, letter grade, early-warning risk category,
    radar metrics, key positive/negative impact drivers, and what-if sensitivity simulations.
    """
    try:
        return analyze_student_performance(student)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Inference error during performance analysis: {str(e)}"
        )


@app.get("/api/student/growth", response_model=StudentPersonalGrowthProfile, tags=["Student Growth"])
def get_student_growth():
    """
    Retrieves the student's personal academic growth trajectory across evaluation terms,
    subject velocities, growth delta, milestones, and strategic recommendations.
    """
    return marks_db.get_personal_growth_profile()


@app.get("/api/cohort/summary", response_model=CohortSummary, tags=["Cohort Intelligence"])
def get_cohort_summary():
    """
    Computes cohort-level KPIs, passing rates, risk tier distributions,
    subject benchmarking averages, and study-hours vs. exam score scatter points.
    """
    return marks_db.get_cohort_summary()


@app.get("/api/students", response_model=List[StudentListItem], tags=["Student Directory"])
def get_students(
    search: Optional[str] = Query(None, description="Search by student name or student ID"),
    risk: Optional[str] = Query(None, description="Filter by risk category (e.g. Critical Intervention, Moderate Risk, On Track, High Achiever)")
):
    """Retrieves all registered students in the cohort with optional keyword search and risk tier filtering."""
    return marks_db.list_cohort_students(search=search, risk=risk)


@app.get("/api/students/{student_id}", tags=["Student Directory"])
def get_student_by_id(student_id: str):
    """Retrieves full student profile and historical indicators by student ID."""
    student = marks_db.get_cohort_student_by_id(student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID '{student_id}' was not found in the registry."
        )
    return student


@app.post("/api/students", status_code=status.HTTP_201_CREATED, tags=["Student Directory"])
def create_student(new_student: NewStudentInput):
    """Registers a new student profile and calculates their initial performance metrics and marksheet."""
    try:
        created = marks_db.add_cohort_student(new_student)
        return created
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to register new student: {str(e)}"
        )


# ==============================================================================
# Marks Entry Portal & Official Report Cards
# ==============================================================================

@app.post("/api/marks/submit", response_model=StudentMarksReport, tags=["Marks Portal"])
def submit_student_marks(entry: StudentMarksEntry):
    """
    Primary Marks Portal Endpoint:
    Accepts student details, individual subject marks (Math, Science, English, Social Studies, CS),
    and learning attributes. Saves the record and returns an instant comprehensive marksheet report card.
    """
    try:
        report = marks_db.save_student_marks(entry)
        return report
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to process student marks: {str(e)}"
        )


@app.get("/api/marks/records", tags=["Marks Portal"])
def list_marks_records(
    search: Optional[str] = Query(None, description="Search by student name or roll number"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by PASS, FAIL, or all")
):
    """Retrieves student marks records for the class ledger table."""
    return marks_db.list_all_marks_records(search=search, status=status_filter)


@app.get("/api/marks/records/{roll_no}", response_model=StudentMarksReport, tags=["Marks Portal"])
def get_student_report_card(roll_no: str):
    """Retrieves individual official marksheet report card by roll number."""
    report = marks_db.get_student_report(roll_no)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report card for Roll No '{roll_no}' was not found."
        )
    return report


@app.delete("/api/marks/records/{roll_no}", tags=["Marks Portal"])
def delete_student_record(roll_no: str):
    """Removes a student record from the portal registry."""
    success = marks_db.delete_student(roll_no)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with Roll No '{roll_no}' not found."
        )
    return {"message": f"Student '{roll_no}' successfully removed from registry."}


@app.get("/api/marks/summary", response_model=ClassMarksSummary, tags=["Marks Portal"])
def get_class_marks_summary():
    """Retrieves class-level subject averages, toppers, and pass/fail statistics."""
    return marks_db.get_class_summary()


# ==============================================================================
# Static Frontend Serving
# ==============================================================================

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/", include_in_schema=False)
    async def serve_portal():
        index_file = FRONTEND_DIR / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        return {"message": "Frontend index.html not found."}
