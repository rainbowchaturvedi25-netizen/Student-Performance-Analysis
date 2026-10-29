/**
 * API Client for Student Performance Analysis Platform.
 * Interacts with FastAPI backend endpoints and records request/response telemetry.
 */

class ApiClient {
  constructor(baseUrl = '') {
    this.baseUrl = baseUrl;
    this.lastTelemetry = {
      endpoint: '/api/analyze',
      method: 'POST',
      status: 200,
      durationMs: 0,
      timestamp: new Date().toLocaleTimeString(),
      requestPayload: null,
      responsePayload: null,
    };
    this.listeners = [];
  }

  onTelemetryUpdate(callback) {
    this.listeners.push(callback);
  }

  notifyTelemetry() {
    this.listeners.forEach((cb) => cb(this.lastTelemetry));
  }

  async _request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`;
    const startTime = performance.now();
    const method = options.method || 'GET';
    const reqBody = options.body ? JSON.parse(options.body) : null;

    try {
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...(options.headers || {}),
        },
        ...options,
      });

      const endTime = performance.now();
      const durationMs = Math.round(endTime - startTime);

      let data;
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        data = await response.json();
      } else {
        data = await response.text();
      }

      // Record telemetry for live API Console
      this.lastTelemetry = {
        endpoint,
        method,
        status: response.status,
        durationMs,
        timestamp: new Date().toLocaleTimeString(),
        requestPayload: reqBody,
        responsePayload: data,
        success: response.ok,
      };
      this.notifyTelemetry();

      if (!response.ok) {
        throw new Error(data.detail || data.error || `HTTP error ${response.status}`);
      }

      return data;
    } catch (err) {
      const endTime = performance.now();
      this.lastTelemetry = {
        endpoint,
        method,
        status: 500,
        durationMs: Math.round(endTime - startTime),
        timestamp: new Date().toLocaleTimeString(),
        requestPayload: reqBody,
        responsePayload: { error: err.message },
        success: false,
      };
      this.notifyTelemetry();
      throw err;
    }
  }

  async healthCheck() {
    return this._request('/api/health');
  }

  async analyzeStudent(studentData) {
    return this._request('/api/analyze', {
      method: 'POST',
      body: JSON.stringify(studentData),
    });
  }

  async getCohortSummary() {
    return this._request('/api/cohort/summary');
  }

  async getStudentGrowth() {
    return this._request('/api/student/growth');
  }

  async getStudents(search = '', risk = '') {
    const params = new URLSearchParams();
    if (search) params.append('search', search);
    if (risk && risk !== 'all') params.append('risk', risk);
    const queryString = params.toString() ? `?${params.toString()}` : '';
    return this._request(`/api/students${queryString}`);
  }

  async getStudentById(studentId) {
    return this._request(`/api/students/${encodeURIComponent(studentId)}`);
  }

  async addStudent(studentData) {
    return this._request('/api/students', {
      method: 'POST',
      body: JSON.stringify(studentData),
    });
  }

  async submitMarks(entryData) {
    return this._request('/api/marks/submit', {
      method: 'POST',
      body: JSON.stringify(entryData),
    });
  }

  async getMarksRecords(search = '', status = '') {
    const params = new URLSearchParams();
    if (search) params.append('search', search);
    if (status && status !== 'all') params.append('status', status);
    const queryString = params.toString() ? `?${params.toString()}` : '';
    return this._request(`/api/marks/records${queryString}`);
  }

  async getMarksReport(rollNo) {
    return this._request(`/api/marks/records/${encodeURIComponent(rollNo)}`);
  }

  async deleteMarksRecord(rollNo) {
    return this._request(`/api/marks/records/${encodeURIComponent(rollNo)}`, {
      method: 'DELETE',
    });
  }

  async getClassMarksSummary() {
    return this._request('/api/marks/summary');
  }

  // Authentication Endpoints (Local Database)
  async login(username, password, currentSemester = null) {
    const body = { username, password };
    if (currentSemester !== null) body.current_semester = currentSemester;
    return this._request('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify(body),
    });
  }

  async register(userData) {
    return this._request('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async getCurrentUser(token) {
    const q = token ? `?token=${encodeURIComponent(token)}` : '';
    return this._request(`/api/auth/me${q}`);
  }

  // All-Semesters & Placement Evaluation Endpoints (Local Database)
  async getAllSemesters(studentId = '') {
    const q = studentId ? `?student_id=${encodeURIComponent(studentId)}` : '';
    return this._request(`/api/student/semesters${q}`);
  }

  async updateSemesterMarks(semesterNum, marks, studentId = '') {
    return this._request('/api/student/semesters/update', {
      method: 'POST',
      body: JSON.stringify({ student_id: studentId, semester_num: semesterNum, marks }),
    });
  }

  async loadSemesterPreset(presetName, studentId = '') {
    const q = studentId ? `?student_id=${encodeURIComponent(studentId)}` : '';
    return this._request(`/api/student/semesters/preset/${encodeURIComponent(presetName)}${q}`, {
      method: 'POST',
    });
  }

  async evaluateCustomPlacement(payload) {
    return this._request('/api/placement/evaluate', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  // Groq AI Analysis Endpoints
  async groqAnalyze(payload) {
    return this._request('/api/groq/analyze', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async getStudentAspirations(studentId = '') {
    const q = studentId ? `?student_id=${encodeURIComponent(studentId)}` : '';
    return this._request(`/api/student/aspirations${q}`);
  }
}

// Global API instance
window.api = new ApiClient();

