"""
Persistent Local SQLite Database for Student Performance & Placement Portal.
Stores user credentials, student profiles, semester subject marks,
calculates SGPA and cumulative CGPA, and maintains placement eligibility states.
"""

import sqlite3
import hashlib
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from .models import (
    SemesterSubjectDetail,
    SemesterDetail,
    PlacementEligibilityResult,
    StudentAllSemestersResponse,
)
from .engine import marks_to_grade_point, compute_semester_sgpa, evaluate_placement_eligibility

DB_FILE = Path(__file__).resolve().parent.parent / "student_records.db"

# 8 Semesters Default Engineering Curriculum (CSE)
STANDARD_CURRICULUM = [
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


def hash_password(password: str) -> str:
    """Hashes password with SHA-256 and fixed salt."""
    salt = "edumetric_ai_secure_salt_2026"
    return hashlib.sha256(f"{salt}{password}".encode("utf-8")).hexdigest()


class LocalDatabase:
    def __init__(self, db_path: Path = DB_FILE):
        self.db_path = db_path
        self._init_tables()
        self._seed_default_users()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_tables(self):
        """Creates SQLite tables if they do not exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 1. Users table (Student and Educator accounts)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    full_name TEXT NOT NULL,
                    student_id TEXT UNIQUE NOT NULL,
                    program TEXT DEFAULT 'B.Tech Computer Science & Engineering',
                    batch TEXT DEFAULT '2022 - 2026',
                    current_semester INTEGER DEFAULT 6,
                    desired_role TEXT DEFAULT 'Full Stack Developer',
                    skills TEXT DEFAULT 'Python, React, Node.js, SQL, DSA',
                    role TEXT DEFAULT 'student',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Ensure columns exist if table was already created
            for col, col_type in [("current_semester", "INTEGER DEFAULT 6"), ("desired_role", "TEXT DEFAULT 'Full Stack Developer'"), ("skills", "TEXT DEFAULT 'Python, React, Node.js, SQL, DSA'")]:
                try:
                    cursor.execute(f"ALTER TABLE users ADD COLUMN {col} {col_type};")
                except sqlite3.OperationalError:
                    pass  # Column already exists

            # 2. Semester Subjects table (Course-level marks and credits)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS semester_subjects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id TEXT NOT NULL,
                    semester_num INTEGER NOT NULL,
                    code TEXT NOT NULL,
                    name TEXT NOT NULL,
                    credits REAL NOT NULL DEFAULT 4.0,
                    marks REAL NOT NULL DEFAULT 0.0,
                    grade_point INTEGER NOT NULL DEFAULT 0,
                    grade_letter TEXT NOT NULL DEFAULT 'F',
                    passed INTEGER NOT NULL DEFAULT 1,
                    remarks TEXT DEFAULT '',
                    UNIQUE(student_id, semester_num, code)
                );
            """)

            # 3. Active Sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    token TEXT PRIMARY KEY,
                    student_id TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            conn.commit()

    def _seed_default_users(self):
        """Seeds initial student accounts and their 8-semester marks if database is fresh."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as cnt FROM users;")
            row = cursor.fetchone()
            if row and row["cnt"] > 0:
                return  # Database already seeded

            # Seed 1: Aarav Sharma (High Achiever, Green Light)
            self.create_user_internal(
                conn,
                username="aarav",
                password="password123",
                full_name="Aarav Sharma",
                student_id="STU-2026",
                program="B.Tech Computer Science & Engineering",
                batch="2022 - 2026"
            )
            self.seed_curriculum_marks(conn, "STU-2026", STANDARD_CURRICULUM)

            # Seed 2: Priya Patel (Caution, Yellow Light)
            self.create_user_internal(
                conn,
                username="priya",
                password="password123",
                full_name="Priya Patel",
                student_id="STU-2027",
                program="B.Tech Computer Science & Engineering",
                batch="2022 - 2026"
            )
            caution_curriculum = self._create_variant_curriculum([58.0, 64.0, 56.0, 62.0, 55.0])
            self.seed_curriculum_marks(conn, "STU-2027", caution_curriculum)

            # Seed 3: Rohit Verma (Ineligible with Backlogs, Red Light)
            self.create_user_internal(
                conn,
                username="rohit",
                password="password123",
                full_name="Rohit Verma",
                student_id="STU-2028",
                program="B.Tech Computer Science & Engineering",
                batch="2022 - 2026"
            )
            red_curriculum = self._create_variant_curriculum([52.0, 50.0, 48.0, 54.0, 50.0], backlogs=[(3, 0), (3, 2), (5, 1)])
            self.seed_curriculum_marks(conn, "STU-2028", red_curriculum)

            conn.commit()

    def _create_variant_curriculum(self, base_scores: List[float], backlogs: List[Tuple[int, int]] = None) -> List[Dict[str, Any]]:
        import copy
        cur = copy.deepcopy(STANDARD_CURRICULUM)
        backlog_set = set(backlogs or [])
        for sem in cur:
            s_num = sem["semester_num"]
            for idx, sub in enumerate(sem["subjects"]):
                if (s_num, idx) in backlog_set:
                    sub["marks"] = 32.0  # Backlog / Fail
                else:
                    sub["marks"] = base_scores[idx % len(base_scores)]
        return cur

    def create_user_internal(self, conn: sqlite3.Connection, username: str, password: str, full_name: str, student_id: str, program: str, batch: str):
        cursor = conn.cursor()
        pwd_hash = hash_password(password)
        cursor.execute("""
            INSERT OR IGNORE INTO users (username, password_hash, full_name, student_id, program, batch)
            VALUES (?, ?, ?, ?, ?, ?);
        """, (username.strip().lower(), pwd_hash, full_name.strip(), student_id.strip(), program.strip(), batch.strip()))

    def seed_curriculum_marks(self, conn: sqlite3.Connection, student_id: str, curriculum: List[Dict[str, Any]]):
        cursor = conn.cursor()
        for sem in curriculum:
            s_num = sem["semester_num"]
            for sub in sem["subjects"]:
                m = float(sub["marks"])
                cr = float(sub.get("credits", 4.0))
                gp, letter, rem, passed = marks_to_grade_point(m)
                cursor.execute("""
                    INSERT OR REPLACE INTO semester_subjects 
                    (student_id, semester_num, code, name, credits, marks, grade_point, grade_letter, passed, remarks)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (student_id, s_num, sub["code"], sub["name"], cr, m, gp, letter, 1 if passed else 0, rem))

    # ==========================================================================
    # Authentication & User Management
    # ==========================================================================

    def register_user(self, username: str, password: str, full_name: str, student_id: str, program: str = "B.Tech Computer Science & Engineering", batch: str = "2022 - 2026", current_semester: int = 5) -> Dict[str, Any]:
        """Registers a new student user in the SQLite database and populates their initial 8 semesters."""
        clean_user = username.strip().lower()
        clean_id = student_id.strip().upper()
        if not clean_user or not password:
            raise ValueError("Username and password are required.")
        if not full_name.strip():
            raise ValueError("Full Name is required.")

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username = ? OR student_id = ?;", (clean_user, clean_id))
            if cursor.fetchone():
                raise ValueError(f"User with username '{clean_user}' or Student ID '{clean_id}' already exists.")

            pwd_hash = hash_password(password)
            cursor.execute("""
                INSERT INTO users (username, password_hash, full_name, student_id, program, batch, current_semester)
                VALUES (?, ?, ?, ?, ?, ?, ?);
            """, (clean_user, pwd_hash, full_name.strip(), clean_id, program.strip(), batch.strip(), current_semester))

            # Initialize 8 semesters for this new student with baseline curriculum marks
            self.seed_curriculum_marks(conn, clean_id, STANDARD_CURRICULUM)
            conn.commit()

        token = hashlib.sha256(f"{clean_id}_{os.urandom(16)}".encode()).hexdigest()
        self.save_session(token, clean_id)

        return {
            "token": token,
            "username": clean_user,
            "full_name": full_name.strip(),
            "student_id": clean_id,
            "program": program.strip(),
            "batch": batch.strip(),
            "current_semester": current_semester,
        }

    def authenticate_user(self, username: str, password: str, current_semester: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Verifies credentials against local SQLite database. Optionally updates current_semester."""
        clean_user = username.strip().lower()
        pwd_hash = hash_password(password)

        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Allow login by username OR by student_id
            cursor.execute("""
                SELECT id, username, full_name, student_id, program, batch, role, password_hash, current_semester
                FROM users 
                WHERE username = ? OR student_id = ?;
            """, (clean_user, clean_user.upper()))
            row = cursor.fetchone()
            if not row:
                return None

            if row["password_hash"] != pwd_hash:
                return None

            saved_semester = row["current_semester"] or 5

            # If student provided a semester on login, update and use it
            if current_semester is not None:
                cursor.execute(
                    "UPDATE users SET current_semester = ? WHERE student_id = ?;",
                    (current_semester, row["student_id"])
                )
                conn.commit()
                saved_semester = current_semester

            token = hashlib.sha256(f"{row['student_id']}_{os.urandom(16)}".encode()).hexdigest()
            self.save_session(token, row["student_id"])

            return {
                "token": token,
                "username": row["username"],
                "full_name": row["full_name"],
                "student_id": row["student_id"],
                "program": row["program"],
                "batch": row["batch"],
                "role": row["role"],
                "current_semester": saved_semester,
            }

    def save_session(self, token: str, student_id: str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO sessions (token, student_id) VALUES (?, ?);", (token, student_id))
            conn.commit()

    def get_user_by_token(self, token: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT u.id, u.username, u.full_name, u.student_id, u.program, u.batch, u.role
                FROM sessions s
                JOIN users u ON s.student_id = u.student_id
                WHERE s.token = ?;
            """, (token,))
            row = cursor.fetchone()
            if row:
                return dict(row)
        return None

    def get_user_by_id(self, student_id: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, username, full_name, student_id, program, batch, role, current_semester, desired_role, skills
                FROM users WHERE student_id = ? OR username = ?;
            """, (student_id.strip(), student_id.strip().lower()))
            row = cursor.fetchone()
            if row:
                return dict(row)
        return None

    def update_student_aspirations(self, student_id: str, current_semester: int, desired_role: str, skills: List[str]):
        """Persists student's current semester, target career role and skills into SQLite database."""
        skills_str = ", ".join(skills) if isinstance(skills, list) else str(skills)
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users
                SET current_semester = ?, desired_role = ?, skills = ?
                WHERE student_id = ? OR username = ?;
            """, (current_semester, desired_role.strip(), skills_str, student_id.strip(), student_id.strip().lower()))
            conn.commit()

    def get_student_aspirations(self, student_id: str) -> Dict[str, Any]:
        """Retrieves student's current semester, desired role, and skills from SQLite."""
        user = self.get_user_by_id(student_id)
        if user:
            raw_skills = user.get("skills") or "Python, React, Node.js, SQL, DSA"
            skills_list = [s.strip() for s in raw_skills.split(",") if s.strip()]
            return {
                "current_semester": user.get("current_semester") or 6,
                "desired_role": user.get("desired_role") or "Full Stack Developer",
                "skills": skills_list,
            }
        return {
            "current_semester": 6,
            "desired_role": "Full Stack Developer",
            "skills": ["Python", "React", "Node.js", "SQL", "DSA"],
        }

    # ==========================================================================
    # Semesters & Marks Persistence
    # ==========================================================================

    def get_student_all_semesters(self, student_id: str = "STU-2026") -> StudentAllSemestersResponse:
        """
        Reads from local SQLite database:
        - Retrieves all course marks for each of the 8 semesters
        - Computes each semester's SGPA
        - Computes Cumulative Average CGPA across all semesters
        - Evaluates Placement Eligibility (Green, Yellow, Red traffic lights)
        """
        user = self.get_user_by_id(student_id)
        if not user:
            # Fallback to default Aarav Sharma STU-2026
            user = self.get_user_by_id("STU-2026")
            if not user:
                user = {
                    "student_id": student_id,
                    "full_name": "Active Student",
                    "program": "B.Tech Computer Science & Engineering",
                    "batch": "2022 - 2026"
                }

        real_id = user["student_id"]
        semester_details: List[SemesterDetail] = []
        total_weighted_sgpa = 0.0
        total_credits = 0.0
        total_earned_credits = 0.0
        total_backlogs = 0

        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Fetch subjects grouped by semester
            cursor.execute("""
                SELECT semester_num, code, name, credits, marks, grade_point, grade_letter, passed, remarks
                FROM semester_subjects
                WHERE student_id = ?
                ORDER BY semester_num ASC, code ASC;
            """, (real_id,))
            rows = cursor.fetchall()

            # Group subjects by semester
            sem_map: Dict[int, List[Dict[str, Any]]] = {}
            for r in rows:
                s_num = r["semester_num"]
                if s_num not in sem_map:
                    sem_map[s_num] = []
                sem_map[s_num].append(dict(r))

            # Ensure all 8 semesters exist
            for s_num in range(1, 9):
                raw_subs = sem_map.get(s_num, [])
                if not raw_subs:
                    # Seed standard curriculum for this semester if missing
                    matching_def = next((x for x in STANDARD_CURRICULUM if x["semester_num"] == s_num), None)
                    if matching_def:
                        raw_subs = matching_def["subjects"]
                        for sb in raw_subs:
                            m = float(sb["marks"])
                            cr = float(sb.get("credits", 4.0))
                            gp, letter, rem, passed = marks_to_grade_point(m)
                            cursor.execute("""
                                INSERT OR REPLACE INTO semester_subjects 
                                (student_id, semester_num, code, name, credits, marks, grade_point, grade_letter, passed, remarks)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                            """, (real_id, s_num, sb["code"], sb["name"], cr, m, gp, letter, 1 if passed else 0, rem))
                        conn.commit()

                sem_res = compute_semester_sgpa(raw_subs)
                sub_objs = [SemesterSubjectDetail(**s) for s in sem_res["subjects"]]

                credits_earned = sum(s["credits"] for s in sem_res["subjects"] if s["passed"])
                total_earned_credits += credits_earned
                total_credits += sem_res["total_credits"]
                total_weighted_sgpa += (sem_res["sgpa"] * sem_res["total_credits"])
                total_backlogs += sem_res["backlogs_count"]

                semester_details.append(
                    SemesterDetail(
                        semester_num=s_num,
                        semester_id=f"sem-{s_num}",
                        semester_name=f"Semester {s_num}",
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
            student_id=user["student_id"],
            student_name=user["full_name"],
            program=user.get("program", "B.Tech Computer Science & Engineering"),
            batch=user.get("batch", "2022 - 2026"),
            total_semesters=len(semester_details),
            active_semester=1,
            semesters=semester_details,
            avg_cgpa=avg_cgpa,
            highest_sgpa=highest_sgpa,
            lowest_sgpa=lowest_sgpa,
            total_credits=total_credits,
            total_backlogs=total_backlogs,
            placement=placement_res,
        )

    def update_semester_marks(self, student_id: str, semester_num: int, marks: Dict[str, float]) -> StudentAllSemestersResponse:
        """
        Saves updated marks into local SQLite database for the student,
        and recomputes all SGPA and Placement indicators.
        """
        user = self.get_user_by_id(student_id)
        real_id = user["student_id"] if user else student_id

        with self.get_connection() as conn:
            cursor = conn.cursor()
            for code, new_val in marks.items():
                m = max(0.0, min(100.0, float(new_val)))
                gp, letter, rem, passed = marks_to_grade_point(m)
                cursor.execute("""
                    UPDATE semester_subjects
                    SET marks = ?, grade_point = ?, grade_letter = ?, passed = ?, remarks = ?
                    WHERE student_id = ? AND semester_num = ? AND (code = ? OR LOWER(code) = ?);
                """, (m, gp, letter, 1 if passed else 0, rem, real_id, semester_num, code, code.lower()))
            conn.commit()

        return self.get_student_all_semesters(real_id)

    def apply_preset(self, student_id: str, preset_name: str) -> StudentAllSemestersResponse:
        """Applies high-achiever, caution, or remedial preset into local SQLite database."""
        user = self.get_user_by_id(student_id)
        real_id = user["student_id"] if user else student_id
        p = preset_name.lower().strip()

        with self.get_connection() as conn:
            cursor = conn.cursor()
            if p in ["green", "high_achiever", "eligible"]:
                base_scores = [88.0, 92.0, 85.0, 90.0, 94.0]
                cursor.execute("SELECT id, semester_num, code FROM semester_subjects WHERE student_id = ? ORDER BY semester_num, id;", (real_id,))
                rows = cursor.fetchall()
                for idx, r in enumerate(rows):
                    m = min(100.0, base_scores[idx % len(base_scores)] + (r["semester_num"] % 3) * 2.0)
                    gp, letter, rem, passed = marks_to_grade_point(m)
                    cursor.execute("UPDATE semester_subjects SET marks = ?, grade_point = ?, grade_letter = ?, passed = ? WHERE id = ?;", (m, gp, letter, 1 if passed else 0, r["id"]))
            elif p in ["yellow", "caution", "borderline"]:
                caution_scores = [58.0, 64.0, 56.0, 62.0, 55.0]
                cursor.execute("SELECT id, semester_num, code FROM semester_subjects WHERE student_id = ? ORDER BY semester_num, id;", (real_id,))
                rows = cursor.fetchall()
                for idx, r in enumerate(rows):
                    m = caution_scores[idx % len(caution_scores)]
                    gp, letter, rem, passed = marks_to_grade_point(m)
                    cursor.execute("UPDATE semester_subjects SET marks = ?, grade_point = ?, grade_letter = ?, passed = ? WHERE id = ?;", (m, gp, letter, 1 if passed else 0, r["id"]))
            elif p in ["red", "at_risk", "ineligible"]:
                cursor.execute("SELECT id, semester_num, code FROM semester_subjects WHERE student_id = ? ORDER BY semester_num, id;", (real_id,))
                rows = cursor.fetchall()
                for r in rows:
                    if r["semester_num"] == 3 and r["code"] in ["CS301", "CS304"]:
                        m = 32.0  # Backlog
                    elif r["semester_num"] == 5 and r["code"] == "CS502":
                        m = 34.0  # Backlog
                    else:
                        m = 52.0  # Marginal pass
                    gp, letter, rem, passed = marks_to_grade_point(m)
                    cursor.execute("UPDATE semester_subjects SET marks = ?, grade_point = ?, grade_letter = ?, passed = ? WHERE id = ?;", (m, gp, letter, 1 if passed else 0, r["id"]))
            elif p in ["default", "reset"]:
                cursor.execute("DELETE FROM semester_subjects WHERE student_id = ?;", (real_id,))
                self.seed_curriculum_marks(conn, real_id, STANDARD_CURRICULUM)

            conn.commit()

        return self.get_student_all_semesters(real_id)


# Global Database Singleton
db = LocalDatabase()

