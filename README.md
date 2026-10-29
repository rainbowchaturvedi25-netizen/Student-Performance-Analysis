# ✦ EduMetrics AI · Student Performance Analysis Prototype

A full-stack prototype for **Student Performance Analysis & Early Warning Risk Prediction**, connecting an interactive glassmorphic web frontend to a FastAPI RESTful backend via real-time JSON APIs.

---

## 🌟 Highlights

- **Predictive Performance & Risk Engine**: Evaluates attendance, assignment averages, exam scores, weekly independent study hours, previous GPA, and sleep hygiene to compute composite performance estimates, letter grades, and risk tiers.
- **Multi-Dimensional Competency Radar**: Live Chart.js radar visualization comparing student capabilities against cohort benchmarks.
- **What-If Sensitivity Simulator**: Instant hypothetical interventions demonstrating how adjustments in study hours, attendance, or assignment focus impact final outcomes.
- **Cohort Analytics & Visualizations**:
  - Cohort Risk Tier Breakdown (Donut Chart)
  - Study Hours vs. Exam Score Correlation (Scatter Plot with risk color-coding)
  - Departmental Subject Benchmarking (Bar Chart)
- **Live Student Roster Management**: Search, filter by risk level, inspect profiles directly into the sandbox, and add new students with instant recalculation.
- **Interactive API Telemetry Console**: Built-in inspector showing live request/response JSON payloads, HTTP status codes, and latency in real time.
- **Interactive Swagger & ReDoc Docs**: Auto-generated interactive API documentation at `/docs` and `/redoc`.

---

## 🏗️ Architecture & Project Structure

```
Student performance project/
│
├── backend/
│   ├── __init__.py           # Backend package initialization
│   ├── models.py             # Pydantic schemas (StudentInput, AnalysisResponse, CohortSummary)
│   ├── engine.py             # Predictive scoring algorithm, risk classification & what-if engine
│   ├── data.py               # In-memory student repository & cohort aggregation logic
│   └── api.py                # FastAPI routes, CORS middleware & static file mounting
│
├── frontend/
│   ├── index.html            # Semantic HTML5 UI with Bento ribbon, tabs & modal dialogs
│   ├── css/
│   │   └── style.css         # Dark slate glassmorphism design system & micro-animations
│   └── js/
│       ├── api.js            # REST API client with built-in telemetry tracking
│       ├── charts.js         # Chart.js radar, donut, scatter, and bar chart handlers
│       └── app.js            # App state manager, slider bindings & event orchestration
│
├── main.py                   # Unified launcher (starts FastAPI server on port 8000)
├── requirements.txt          # Python dependencies (fastapi, uvicorn, pydantic)
└── README.md                 # Project documentation
```

---

## 🚀 Getting Started

### 1. Requirements
- Python 3.10+ (tested on Python 3.15)
- pip

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Start the Application
Run the launcher script from the project root:
```bash
python main.py
```

Open your browser and visit:
- **Web Dashboard**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Swagger API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc Documentation**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🔌 API Endpoints Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Service health status, version, and active student count |
| `POST` | `/api/analyze` | Evaluates student indicators and returns score, grade, risk, drivers & what-if scenarios |
| `GET` | `/api/cohort/summary` | Aggregated statistics, pass rates, risk distributions & correlation scatter points |
| `GET` | `/api/students` | List cohort students with optional `?search=` and `?risk=` filters |
| `GET` | `/api/students/{id}` | Detailed profile and historical indicators for a specific student |
| `POST` | `/api/students` | Registers a new student and automatically calculates baseline metrics |
| `POST` | `/api/marks/submit` | Submits individual subject marks (Math, Science, English, Social, CS) & attributes |
| `GET` | `/api/marks/records` | Lists marks records for the class ledger with optional search & pass/fail filter |
| `GET` | `/api/marks/records/{roll_no}` | Retrieves official academic marksheet transcript by roll number |
| `DELETE` | `/api/marks/records/{roll_no}` | Removes a student record from the portal database |
| `GET` | `/api/marks/summary` | Computes class averages, highest/lowest marks, and pass/remedial distributions |

### Example Predictive Analysis Request (`POST /api/analyze`)
```json
{
  "name": "Elena Rostova",
  "student_id": "STU-1001",
  "attendance": 92.0,
  "assignment_avg": 88.0,
  "exam_score": 85.0,
  "study_hours": 12.0,
  "previous_gpa": 3.6,
  "sleep_hours": 7.5
}
```

### Example Marks Portal Submission (`POST /api/marks/submit`)
```json
{
  "name": "Elena Rostova",
  "roll_no": "STU-1001",
  "grade_class": "Grade 10-A",
  "term": "Midterm Examination",
  "marks": {
    "mathematics": 90.0,
    "science": 88.0,
    "english": 92.0,
    "social_studies": 86.0,
    "computer_science": 94.0
  },
  "attendance": 92.0,
  "study_hours_weekly": 12.0,
  "assignment_completion": 88.0,
  "sleep_hours": 7.5,
  "extracurricular": "High",
  "teacher_remarks": "Outstanding analytical mind."
}
```

