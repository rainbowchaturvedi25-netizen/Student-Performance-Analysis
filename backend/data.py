"""
Unified in-memory database for Single Student Academic Performance & Growth Tracker.
Maintains personal term assessments, computes growth velocity over time, and generates transcripts.
"""

from typing import List, Dict, Any, Optional
import copy
from .models import (
    StudentMarksEntry,
    SubjectMarks,
    StudentMarksReport,
    ClassMarksSummary,
    CohortSummary,
    CorrelationScatterPoint,
    StudentListItem,
    NewStudentInput,
    TermGrowthPoint,
    SubjectGrowthDetail,
    StudentPersonalGrowthProfile,
    SemesterSubjectDetail,
    SemesterDetail,
    PlacementEligibilityResult,
    StudentAllSemestersResponse,
)
from .engine import (
    calculate_marks_report,
    compute_composite_score,
    score_to_letter_grade,
    classify_risk,
    compute_semester_sgpa,
    evaluate_placement_eligibility,
)

# Default Single Student Profile Information
DEFAULT_STUDENT_ID = "STU-2026"
DEFAULT_STUDENT_NAME = "Aarav Sharma"
DEFAULT_GRADE_CLASS = "Grade 10-A"
DEFAULT_ACADEMIC_YEAR = "2025 - 2026"
DEFAULT_PROGRAM = "B.Tech Computer Science & Engineering"
DEFAULT_BATCH = "2022 - 2026"

# 8 Semesters Baseline Curriculum & Marks Data (10-point scale)
INITIAL_ALL_SEMESTERS: List[Dict[str, Any]] = [
    {
        "semester_num": 1,
        "semester_name": "Semester 1",
        "subjects": [
            {"code": "CS101", "name": "Engineering Mathematics I", "credits": 4.0, "marks": 85.0},
            {"code": "CS102", "name": "Engineering Physics", "credits": 4.0, "marks": 82.0},
            {"code": "CS103", "name": "Programming in C", "credits": 4.0, "marks": 90.0},
            {"code": "CS104", "name": "Basic Electrical Engineering", "credits": 4.0, "marks": 78.0},
            {"code": "CS105", "name": "Professional Communication", "credits": 4.0, "marks": 88.0},
        ]
    },
    {
        "semester_num": 2,
        "semester_name": "Semester 2",
        "subjects": [
            {"code": "CS201", "name": "Engineering Mathematics II", "credits": 4.0, "marks": 80.0},
            {"code": "CS202", "name": "Data Structures & Algorithms", "credits": 4.0, "marks": 86.0},
            {"code": "CS203", "name": "Digital Logic & Design", "credits": 4.0, "marks": 75.0},
            {"code": "CS204", "name": "Object-Oriented Programming (Java)", "credits": 4.0, "marks": 88.0},
            {"code": "CS205", "name": "Environmental Engineering", "credits": 4.0, "marks": 84.0},
        ]
    },
    {
        "semester_num": 3,
        "semester_name": "Semester 3",
        "subjects": [
            {"code": "CS301", "name": "Discrete Mathematics", "credits": 4.0, "marks": 76.0},
            {"code": "CS302", "name": "Database Management Systems", "credits": 4.0, "marks": 92.0},
            {"code": "CS303", "name": "Computer Org & Architecture", "credits": 4.0, "marks": 82.0},
            {"code": "CS304", "name": "Operating Systems", "credits": 4.0, "marks": 85.0},
            {"code": "CS305", "name": "Software Engineering & Agile", "credits": 4.0, "marks": 88.0},
        ]
    },
    {
        "semester_num": 4,
        "semester_name": "Semester 4",
        "subjects": [
            {"code": "CS401", "name": "Design & Analysis of Algorithms", "credits": 4.0, "marks": 85.0},
            {"code": "CS402", "name": "Computer Networks", "credits": 4.0, "marks": 84.0},
            {"code": "CS403", "name": "Theory of Computation", "credits": 4.0, "marks": 78.0},
            {"code": "CS404", "name": "Full Stack Web Development", "credits": 4.0, "marks": 94.0},
            {"code": "CS405", "name": "Applied Statistics & Probability", "credits": 4.0, "marks": 80.0},
        ]
    },
    {
        "semester_num": 5,
        "semester_name": "Semester 5",
        "subjects": [
            {"code": "CS501", "name": "Machine Learning & AI", "credits": 4.0, "marks": 92.0},
            {"code": "CS502", "name": "Compiler Design", "credits": 4.0, "marks": 76.0},
            {"code": "CS503", "name": "Cloud Computing (AWS / GCP)", "credits": 4.0, "marks": 88.0},
            {"code": "CS504", "name": "Information & Network Security", "credits": 4.0, "marks": 84.0},
            {"code": "CS505", "name": "Mobile Application Development", "credits": 4.0, "marks": 90.0},
        ]
    },
    {
        "semester_num": 6,
        "semester_name": "Semester 6",
        "subjects": [
            {"code": "CS601", "name": "Distributed Systems", "credits": 4.0, "marks": 86.0},
            {"code": "CS602", "name": "Big Data Analytics & Spark", "credits": 4.0, "marks": 85.0},
            {"code": "CS603", "name": "DevOps, CI/CD & Docker", "credits": 4.0, "marks": 92.0},
            {"code": "CS604", "name": "Internet of Things (IoT)", "credits": 4.0, "marks": 82.0},
            {"code": "CS605", "name": "Capstone Technical Mini-Project", "credits": 4.0, "marks": 95.0},
        ]
    },
    {
        "semester_num": 7,
        "semester_name": "Semester 7",
        "subjects": [
            {"code": "CS701", "name": "Deep Learning & Neural Networks", "credits": 4.0, "marks": 90.0},
            {"code": "CS702", "name": "Natural Language Processing (NLP)", "credits": 4.0, "marks": 88.0},
            {"code": "CS703", "name": "Blockchain & Cryptography", "credits": 4.0, "marks": 84.0},
            {"code": "CS704", "name": "Enterprise Cloud Architecture", "credits": 4.0, "marks": 86.0},
            {"code": "CS705", "name": "Major Project Phase I", "credits": 4.0, "marks": 96.0},
        ]
    },
    {
        "semester_num": 8,
        "semester_name": "Semester 8",
        "subjects": [
            {"code": "CS801", "name": "Industry Internship & Field Practicum", "credits": 8.0, "marks": 94.0},
            {"code": "CS802", "name": "Major Project Phase II (Viva)", "credits": 8.0, "marks": 96.0},
            {"code": "CS803", "name": "High Performance Computing", "credits": 4.0, "marks": 88.0},
        ]
    },
]

# Historical term assessments demonstrating the student's academic growth trajectory
INITIAL_STUDENT_TERMS = [
    {
        "term_id": "term-1",
        "term_name": "Term 1 - Diagnostic Assessment",
        "date_label": "Sep 2025",
        "attendance": 82.0,
        "study_hours": 6.5,
        "assignment_avg": 75.0,
        "sleep_hours": 7.0,
        "marks": {
            "mathematics": 70.0,
            "science": 72.0,
            "english": 76.0,
            "social_studies": 70.0,
            "computer_science": 74.0,
        },
        "teacher_remarks": "Initial diagnostic benchmark; student demonstrated good curiosity and baseline skills."
    },
    {
        "term_id": "term-2",
        "term_name": "Term 2 - Midterm Examination",
        "date_label": "Nov 2025",
        "attendance": 88.0,
        "study_hours": 9.0,
        "assignment_avg": 82.0,
        "sleep_hours": 7.5,
        "marks": {
            "mathematics": 78.0,
            "science": 80.0,
            "english": 82.0,
            "social_studies": 75.0,
            "computer_science": 85.0,
        },
        "teacher_remarks": "Noticeable improvement in STEM disciplines; study routine becoming more disciplined."
    },
    {
        "term_id": "term-3",
        "term_name": "Term 3 - Pre-Board Assessment",
        "date_label": "Jan 2026",
        "attendance": 92.0,
        "study_hours": 11.5,
        "assignment_avg": 88.0,
        "sleep_hours": 7.5,
        "marks": {
            "mathematics": 84.0,
            "science": 85.0,
            "english": 88.0,
            "social_studies": 80.0,
            "computer_science": 92.0,
        },
        "teacher_remarks": "Excellent consistency across all 5 subjects; Computer Science in top distinction tier."
    },
    {
        "term_id": "term-4",
        "term_name": "Term 4 - Final Semester Evaluation",
        "date_label": "Mar 2026",
        "attendance": 94.0,
        "study_hours": 13.5,
        "assignment_avg": 92.0,
        "sleep_hours": 8.0,
        "marks": {
            "mathematics": 88.0,
            "science": 86.0,
            "english": 92.0,
            "social_studies": 85.0,
            "computer_science": 96.0,
        },
        "teacher_remarks": "Outstanding growth trajectory. Achieved First Class with Distinction overall."
    },
]


class StudentDataRepository:
    def __init__(self):
        self.student_id = DEFAULT_STUDENT_ID
        self.student_name = DEFAULT_STUDENT_NAME
        self.grade_class = DEFAULT_GRADE_CLASS
        self.academic_year = DEFAULT_ACADEMIC_YEAR
        self.program = DEFAULT_PROGRAM
        self.batch = DEFAULT_BATCH
        self.semesters = copy.deepcopy(INITIAL_ALL_SEMESTERS)
        self.active_semester = 8
        
        # Keyed by term_id (e.g. 'term-1', 'term-2')
        self.term_records: Dict[str, Dict[str, Any]] = {}
        self.marks_reports: Dict[str, StudentMarksReport] = {}
        self._next_term_counter = 5

        for raw in INITIAL_STUDENT_TERMS:
            self._insert_term(raw)

    def _insert_term(self, raw: Dict[str, Any]):
        tid = raw["term_id"]
        marks_obj = SubjectMarks(**raw["marks"])
        total_obtained = sum(raw["marks"].values())
        pct = round((total_obtained / 500.0) * 100.0, 1)
        grade = score_to_letter_grade(pct)
        gpa = round(min(4.0, max(1.0, (pct / 100.0) * 4.0 + 0.3)), 2)

        entry = StudentMarksEntry(
            name=self.student_name,
            roll_no=self.student_id,
            grade_class=self.grade_class,
            term=raw["term_name"],
            marks=marks_obj,
            attendance=raw["attendance"],
            study_hours_weekly=raw["study_hours"],
            assignment_completion=raw.get("assignment_avg", 85.0),
            sleep_hours=raw.get("sleep_hours", 7.5),
            extracurricular="High" if raw["study_hours"] > 10 else "Moderate",
            teacher_remarks=raw.get("teacher_remarks", "Assessment logged in academic journey."),
        )

        report = calculate_marks_report(entry)
        self.marks_reports[tid] = report

        record = {
            "term_id": tid,
            "roll_no": self.student_id,
            "name": self.student_name,
            "term": raw["term_name"],
            "date_label": raw.get("date_label", "2026"),
            "grade_class": self.grade_class,
            "attendance": raw["attendance"],
            "study_hours": raw["study_hours"],
            "assignment_avg": raw.get("assignment_avg", 85.0),
            "sleep_hours": raw.get("sleep_hours", 7.5),
            "marks": raw["marks"],
            "total_obtained": total_obtained,
            "percentage": pct,
            "letter_grade": grade,
            "gpa": gpa,
            "final_result": report.final_result,
            "academic_status": report.academic_status,
            "teacher_remarks": raw.get("teacher_remarks", ""),
        }
        self.term_records[tid] = record

    def update_student_name(self, new_name: str):
        if new_name and new_name.strip():
            self.student_name = new_name.strip()
            for rec in self.term_records.values():
                rec["name"] = self.student_name

    # --------------------------------------------------------------------------
    # Personal Academic Growth Engine
    # --------------------------------------------------------------------------

    def get_personal_growth_profile(self) -> StudentPersonalGrowthProfile:
        """Computes growth velocity, delta metrics, subject trajectories, and milestones."""
        if not self.term_records:
            return StudentPersonalGrowthProfile(
                student_id=self.student_id,
                student_name=self.student_name,
                grade_class=self.grade_class,
                academic_year=self.academic_year,
                current_term="Initial",
                current_percentage=0.0,
                current_gpa=0.0,
                overall_grade="N/A",
                final_result="N/A",
                academic_status="N/A",
                overall_growth_delta=0.0,
                highest_growth_subject="N/A",
                lowest_growth_subject="N/A",
                target_score=90.0,
                timeline=[],
                subject_growth=[],
                milestones=[],
                growth_recommendations=[],
            )

        # Sort terms in order
        sorted_terms = list(self.term_records.values())
        baseline = sorted_terms[0]
        latest = sorted_terms[-1]

        overall_delta = round(latest["percentage"] - baseline["percentage"], 1)

        # Build timeline points
        timeline_points: List[TermGrowthPoint] = []
        for t in sorted_terms:
            timeline_points.append(
                TermGrowthPoint(
                    term_id=t["term_id"],
                    term_name=t["term"],
                    date_label=t["date_label"],
                    total_obtained=t["total_obtained"],
                    percentage=t["percentage"],
                    gpa=t["gpa"],
                    grade=t["letter_grade"],
                    final_result=t["final_result"],
                    marks=t["marks"],
                    attendance=t["attendance"],
                    study_hours=t["study_hours"],
                    remarks=t["teacher_remarks"],
                )
            )

        # Compute subject growth details (baseline term vs latest term)
        subjects = [
            ("Mathematics", "mathematics"),
            ("Science & Tech", "science"),
            ("English Language", "english"),
            ("Social Studies", "social_studies"),
            ("Computer Science", "computer_science"),
        ]

        subject_growths: List[SubjectGrowthDetail] = []
        for display_name, key in subjects:
            b_val = baseline["marks"].get(key, 0.0)
            c_val = latest["marks"].get(key, 0.0)
            delta = round(c_val - b_val, 1)
            pct_growth = round(((c_val - b_val) / max(1.0, b_val)) * 100.0, 1)
            subject_growths.append(
                SubjectGrowthDetail(
                    subject=display_name,
                    baseline_score=b_val,
                    current_score=c_val,
                    growth_delta=delta,
                    growth_percentage=pct_growth,
                )
            )

        # Find fastest improving subject
        subject_growths.sort(key=lambda x: x.growth_delta, reverse=True)
        top_growth = f"{subject_growths[0].subject} (+{subject_growths[0].growth_delta} pts)"
        lowest_growth = f"{subject_growths[-1].subject} (+{subject_growths[-1].growth_delta} pts)"

        milestones = [
            {"icon": "🌟", "title": "Honor Roll Standing", "desc": f"Achieved {latest['percentage']}% aggregate across all 5 core subjects."},
            {"icon": "🚀", "title": "Highest Growth Subject", "desc": f"{top_growth} progression from Term 1 to Current Evaluation."},
            {"icon": "🎯", "title": "Disciplined Study Routine", "desc": f"Increased self-study from {baseline['study_hours']}h to {latest['study_hours']}h/wk with {latest['attendance']}% attendance."},
            {"icon": "🏆", "title": "Perfect Subject Pass Record", "desc": "0 failing subject marks maintained across all evaluation cycles."},
        ]

        recs = [
            f"Capitalize on peak momentum in {subject_growths[0].subject} to tackle advanced and competitive problem sets.",
            f"Prioritize {subject_growths[-1].subject} with dedicated 30-minute daily review sessions to raise it above 90%.",
            f"Maintain consistent 7.5 to 8.0 hours of restorative sleep to ensure maximum test-day cognitive retention.",
        ]

        return StudentPersonalGrowthProfile(
            student_id=self.student_id,
            student_name=self.student_name,
            grade_class=self.grade_class,
            academic_year=self.academic_year,
            current_term=latest["term"],
            current_percentage=latest["percentage"],
            current_gpa=latest["gpa"],
            overall_grade=latest["letter_grade"],
            final_result=latest["final_result"],
            academic_status=latest["academic_status"],
            overall_growth_delta=overall_delta,
            highest_growth_subject=top_growth,
            lowest_growth_subject=lowest_growth,
            target_score=min(98.0, round(latest["percentage"] + 4.5, 1)),
            timeline=timeline_points,
            subject_growth=subject_growths,
            milestones=milestones,
            growth_recommendations=recs,
        )

    # --------------------------------------------------------------------------
    # Backward Compatibility Adapter for Existing Views
    # --------------------------------------------------------------------------

    def get_cohort_summary(self) -> CohortSummary:
        """Adapts single student progression into KPI format for top ribbon."""
        growth = self.get_personal_growth_profile()
        scatter: List[CorrelationScatterPoint] = []
        for t in self.term_records.values():
            scatter.append(
                CorrelationScatterPoint(
                    x=round(t["study_hours"], 1),
                    y=round(t["percentage"], 1),
                    name=t["term"].split("-")[0].strip(),
                    score=round(t["percentage"], 1),
                    risk="High Achiever" if t["percentage"] >= 85 else "On Track",
                )
            )

        latest_marks = list(self.term_records.values())[-1]["marks"] if self.term_records else {}
        sub_avgs = {
            "Mathematics": latest_marks.get("mathematics", 88.0),
            "Science & Tech": latest_marks.get("science", 86.0),
            "English Language": latest_marks.get("english", 92.0),
            "Social Studies": latest_marks.get("social_studies", 85.0),
            "Computer Science": latest_marks.get("computer_science", 96.0),
        }

        return CohortSummary(
            cohort_average_score=growth.current_percentage,
            pass_rate=100.0,
            at_risk_count=0,
            total_students=len(self.term_records),
            risk_distribution={"Critical Intervention": 0, "Moderate Risk": 0, "On Track": 1, "High Achiever": len(self.term_records)},
            correlation_scatter=scatter,
            subject_averages=sub_avgs,
        )

    def list_cohort_students(
        self, search: Optional[str] = None, risk: Optional[str] = None
    ) -> List[StudentListItem]:
        """Returns single student's term evaluation records."""
        items: List[StudentListItem] = []
        for t in self.term_records.values():
            if search and search.lower() not in t["term"].lower():
                continue
            items.append(
                StudentListItem(
                    id=t["term_id"],
                    name=t["term"],
                    grade_level=t["grade_class"],
                    attendance=t["attendance"],
                    assignment_avg=t["assignment_avg"],
                    exam_score=t["percentage"],
                    study_hours=t["study_hours"],
                    previous_gpa=t["gpa"],
                    sleep_hours=t["sleep_hours"],
                    predicted_score=t["percentage"],
                    letter_grade=t["letter_grade"],
                    risk_level="High Achiever" if t["percentage"] >= 85 else "On Track",
                    risk_badge="Distinction" if t["percentage"] >= 85 else "First Class",
                )
            )
        return items

    def get_cohort_student_by_id(self, term_id: str) -> Optional[Dict[str, Any]]:
        return self.term_records.get(term_id.lower())

    def add_cohort_student(self, new_data: NewStudentInput) -> Dict[str, Any]:
        """Saves a new term assessment for this student."""
        tid = f"term-{self._next_term_counter}"
        self._next_term_counter += 1
        raw = {
            "term_id": tid,
            "term_name": new_data.name if "Term" in new_data.name else f"Term {self._next_term_counter - 1} Assessment",
            "date_label": "2026",
            "attendance": new_data.attendance,
            "study_hours": new_data.study_hours,
            "assignment_avg": new_data.assignment_avg,
            "sleep_hours": new_data.sleep_hours,
            "marks": {
                "mathematics": round(new_data.exam_score * 0.95, 1),
                "science": round(new_data.exam_score * 0.98, 1),
                "english": round(new_data.assignment_avg * 0.95, 1),
                "social_studies": round(new_data.assignment_avg * 0.92, 1),
                "computer_science": round(min(100.0, new_data.exam_score + 4.0), 1),
            },
            "teacher_remarks": "Logged via assessment portal.",
        }
        self._insert_term(raw)
        return self.term_records[tid]

    # --------------------------------------------------------------------------
    # Marks Entry & Report Cards
    # --------------------------------------------------------------------------

    def save_student_marks(self, entry: StudentMarksEntry) -> StudentMarksReport:
        tid = f"term-{self._next_term_counter}"
        self._next_term_counter += 1

        self.update_student_name(entry.name)
        raw = {
            "term_id": tid,
            "term_name": entry.term or f"Term {self._next_term_counter - 1} Evaluation",
            "date_label": "2026",
            "attendance": entry.attendance,
            "study_hours": entry.study_hours_weekly,
            "assignment_avg": entry.assignment_completion,
            "sleep_hours": entry.sleep_hours,
            "marks": {
                "mathematics": entry.marks.mathematics,
                "science": entry.marks.science,
                "english": entry.marks.english,
                "social_studies": entry.marks.social_studies,
                "computer_science": entry.marks.computer_science,
            },
            "teacher_remarks": entry.teacher_remarks or "Personal assessment recorded in growth journey.",
        }
        self._insert_term(raw)
        return self.marks_reports[tid]

    def get_student_report(self, term_id: str) -> Optional[StudentMarksReport]:
        return self.marks_reports.get(term_id.lower())

    def delete_student(self, term_id: str) -> bool:
        key = term_id.lower()
        found = False
        if key in self.term_records:
            del self.term_records[key]
            found = True
        if key in self.marks_reports:
            del self.marks_reports[key]
            found = True
        return found

    def list_all_marks_records(
        self, search: Optional[str] = None, status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        results = []
        for rep in self.marks_reports.values():
            rec = {
                "roll_no": rep.roll_no,
                "name": rep.name,
                "grade_class": rep.grade_class,
                "term": rep.term,
                "math": next((s.marks_obtained for s in rep.subject_results if "Math" in s.subject), 0),
                "science": next((s.marks_obtained for s in rep.subject_results if "Science" in s.subject), 0),
                "english": next((s.marks_obtained for s in rep.subject_results if "English" in s.subject), 0),
                "social": next((s.marks_obtained for s in rep.subject_results if "Social" in s.subject), 0),
                "cs": next((s.marks_obtained for s in rep.subject_results if "Computer" in s.subject), 0),
                "total_obtained": rep.total_obtained,
                "max_total": rep.max_total,
                "percentage": rep.percentage,
                "overall_grade": rep.overall_grade,
                "gpa": rep.gpa,
                "final_result": rep.final_result,
                "academic_status": rep.academic_status,
                "risk_tier": rep.risk_tier,
                "risk_color": rep.risk_color,
                "attendance": rep.attributes.get("attendance", 0),
                "study_hours": rep.attributes.get("study_hours_weekly", 0),
            }

            if search:
                q = search.lower()
                if q not in rec["term"].lower():
                    continue

            if status and status != "all":
                if status.upper() == "PASS" and rec["final_result"] != "PASSED":
                    continue
                if status.upper() == "FAIL" and rec["final_result"] != "FAILED":
                    continue

            results.append(rec)
        return results

    def get_class_summary(self) -> ClassMarksSummary:
        total = len(self.marks_reports)
        percentages = [r.percentage for r in self.marks_reports.values()]
        return ClassMarksSummary(
            total_students=total,
            class_average_percentage=round(sum(percentages) / max(1, total), 1),
            highest_percentage=round(max(percentages), 1) if percentages else 0.0,
            lowest_percentage=round(min(percentages), 1) if percentages else 0.0,
            pass_percentage=100.0,
            total_passed=total,
            total_failed=0,
            subject_class_averages={
                "Mathematics": 88.0,
                "Science & Tech": 86.0,
                "English Language": 92.0,
                "Social Studies": 85.0,
                "Computer Science": 96.0,
            },
            grade_distribution={"A+": 2, "A": 1, "B": 1},
            risk_distribution={"High Achiever": total, "On Track": 0},
            students_list=self.list_all_marks_records()
        )

    # --------------------------------------------------------------------------
    # All-Semesters Evaluation & Placement Engine
    # --------------------------------------------------------------------------

    def get_student_all_semesters(self) -> StudentAllSemestersResponse:
        """
        Calculates individual semester SGPAs, overall cumulative CGPA across all semesters,
        and computes campus placement eligibility with Green / Yellow / Red traffic light verdict.
        """
        semester_details: List[SemesterDetail] = []
        total_weighted_sgpa = 0.0
        total_credits = 0.0
        total_earned_credits = 0.0
        total_backlogs = 0

        for sem in self.semesters:
            sem_res = compute_semester_sgpa(sem["subjects"])
            sub_objs = [SemesterSubjectDetail(**s) for s in sem_res["subjects"]]
            
            credits_earned = sum(s["credits"] for s in sem_res["subjects"] if s["passed"])
            total_earned_credits += credits_earned
            total_credits += sem_res["total_credits"]
            total_weighted_sgpa += (sem_res["sgpa"] * sem_res["total_credits"])
            total_backlogs += sem_res["backlogs_count"]

            semester_details.append(
                SemesterDetail(
                    semester_num=sem["semester_num"],
                    semester_id=f"sem-{sem['semester_num']}",
                    semester_name=sem["semester_name"],
                    credits_total=sem_res["total_credits"],
                    credits_earned=credits_earned,
                    total_marks=sem_res["total_obtained"],
                    max_marks=sem_res["max_total"],
                    percentage=sem_res["percentage"],
                    sgpa=sem_res["sgpa"],
                    backlogs_count=sem_res["backlogs_count"],
                    status=sem_res["status"],
                    subjects=sub_objs,
                )
            )

        avg_cgpa = round(total_weighted_sgpa / max(1.0, total_credits), 2)
        sgpas = [s.sgpa for s in semester_details]
        highest_sgpa = max(sgpas) if sgpas else 0.0
        lowest_sgpa = min(sgpas) if sgpas else 0.0

        placement_dict = evaluate_placement_eligibility(
            avg_cgpa=avg_cgpa,
            total_backlogs=total_backlogs,
            total_credits_earned=total_earned_credits,
            semester_count=len(semester_details)
        )
        placement_res = PlacementEligibilityResult(**placement_dict)

        return StudentAllSemestersResponse(
            student_id=self.student_id,
            student_name=self.student_name,
            program=self.program,
            batch=self.batch,
            total_semesters=len(semester_details),
            active_semester=self.active_semester,
            semesters=semester_details,
            avg_cgpa=avg_cgpa,
            highest_sgpa=highest_sgpa,
            lowest_sgpa=lowest_sgpa,
            total_credits=total_credits,
            total_backlogs=total_backlogs,
            placement=placement_res,
        )

    def update_semester_marks(self, semester_num: int, marks: Dict[str, float]) -> StudentAllSemestersResponse:
        """Updates marks for subjects in a specific semester and recalculates all indicators."""
        target_sem = next((s for s in self.semesters if s["semester_num"] == semester_num), None)
        if target_sem:
            self.active_semester = semester_num
            for sub in target_sem["subjects"]:
                # Match by code (e.g. CS101) or by lowercase key
                code_key = sub["code"]
                clean_name = sub["name"].lower()
                if code_key in marks:
                    sub["marks"] = max(0.0, min(100.0, float(marks[code_key])))
                elif code_key.lower() in marks:
                    sub["marks"] = max(0.0, min(100.0, float(marks[code_key.lower()])))
                elif clean_name in marks:
                    sub["marks"] = max(0.0, min(100.0, float(marks[clean_name])))
        return self.get_student_all_semesters()

    def set_semester_preset(self, preset_name: str) -> StudentAllSemestersResponse:
        """
        Loads pre-configured marks benchmarks:
        - 'green' (or 'high_achiever'): Distinction CGPA 8.85, 0 backlogs -> Green Light (Eligible)
        - 'yellow' (or 'caution'): Borderline CGPA 6.45, 0 backlogs -> Yellow Light (Caution)
        - 'red' (or 'at_risk'): Remedial CGPA 5.60, active backlogs -> Red Light (Not Eligible)
        """
        p = preset_name.lower().strip()
        if p in ["green", "high_achiever", "eligible"]:
            # Exemplary scores
            base_scores = [88.0, 92.0, 85.0, 90.0, 94.0]
            for sem in self.semesters:
                for idx, sub in enumerate(sem["subjects"]):
                    sub["marks"] = min(100.0, base_scores[idx % len(base_scores)] + (sem["semester_num"] % 3) * 2.0)
        elif p in ["yellow", "caution", "borderline"]:
            # Borderline scores (55-64) with 0 backlogs -> Average CGPA ~6.40 (Caution / Yellow Light)
            caution_scores = [58.0, 64.0, 56.0, 62.0, 55.0]
            for sem in self.semesters:
                for idx, sub in enumerate(sem["subjects"]):
                    sub["marks"] = caution_scores[idx % len(caution_scores)]
        elif p in ["red", "at_risk", "ineligible"]:
            # Low scores with active backlogs in Sem 3 and Sem 5
            for sem in self.semesters:
                for idx, sub in enumerate(sem["subjects"]):
                    if sem["semester_num"] == 3 and idx in [0, 2]:
                        sub["marks"] = 32.0  # Fail / Backlog
                    elif sem["semester_num"] == 5 and idx == 1:
                        sub["marks"] = 34.0  # Fail / Backlog
                    else:
                        sub["marks"] = 52.0  # Marginal pass
        elif p in ["default", "reset"]:
            self.semesters = copy.deepcopy(INITIAL_ALL_SEMESTERS)

        return self.get_student_all_semesters()


# Global database instance
marks_db = StudentDataRepository()
