/**
 * Charting subsystem using Chart.js.
 * Visualizes student competency radar, cohort risk distribution, study-score correlation, and subject averages.
 */

class PerformanceCharts {
  constructor() {
    this.radarChart = null;
    this.riskDonutChart = null;
    this.scatterChart = null;
    this.subjectBarChart = null;
    this.growthLineChart = null;
    this.subjectGrowthBarChart = null;
  }

  // Set default Chart.js styling for Crisp Light theme
  initDefaults() {
    if (typeof Chart === 'undefined') return;

    Chart.defaults.color = '#475569';
    Chart.defaults.font.family = "'Inter', sans-serif";
    Chart.defaults.font.size = 12;
    Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(15, 23, 42, 0.95)';
    Chart.defaults.plugins.tooltip.titleColor = '#ffffff';
    Chart.defaults.plugins.tooltip.bodyColor = '#f1f5f9';
    Chart.defaults.plugins.tooltip.borderColor = 'rgba(255, 255, 255, 0.15)';
    Chart.defaults.plugins.tooltip.borderWidth = 1;
    Chart.defaults.plugins.tooltip.padding = 10;
    Chart.defaults.plugins.tooltip.cornerRadius = 8;
  }

  renderRadar(canvasId, studentMetrics) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    if (this.radarChart) {
      this.radarChart.destroy();
    }

    // Normalized metrics out of 100
    const att = studentMetrics.attendance || 0;
    const exm = studentMetrics.exam_score || 0;
    const asg = studentMetrics.assignment_avg || 0;
    const hrs = Math.min(100, ((studentMetrics.study_hours || 0) / 20) * 100);
    const slp = Math.min(100, ((studentMetrics.sleep_hours || 7) / 9) * 100);

    this.radarChart = new Chart(ctx, {
      type: 'radar',
      data: {
        labels: ['Attendance', 'Exam Mastery', 'Assignments', 'Study Routine', 'Rest & Focus'],
        datasets: [
          {
            label: 'Current Competency',
            data: [att, exm, asg, hrs, slp],
            backgroundColor: 'rgba(79, 70, 229, 0.18)',
            borderColor: '#4f46e5',
            pointBackgroundColor: '#4f46e5',
            pointBorderColor: '#fff',
            pointHoverBackgroundColor: '#fff',
            pointHoverBorderColor: '#4f46e5',
            borderWidth: 2,
          },
          {
            label: 'Cohort Benchmark',
            data: [82, 75, 78, 65, 75],
            backgroundColor: 'rgba(100, 116, 139, 0.06)',
            borderColor: 'rgba(100, 116, 139, 0.4)',
            borderDash: [4, 4],
            pointRadius: 2,
            borderWidth: 1.5,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          r: {
            angleLines: { color: 'rgba(0, 0, 0, 0.08)' },
            grid: { color: 'rgba(0, 0, 0, 0.06)' },
            suggestedMin: 30,
            suggestedMax: 100,
            ticks: {
              display: false,
              stepSize: 20,
            },
            pointLabels: {
              color: '#334155',
              font: { size: 11, weight: '600' },
            },
          },
        },
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              boxWidth: 12,
              padding: 14,
              color: '#475569',
              font: { weight: '500' },
            },
          },
        },
      },
    });
  }

  renderGrowthCharts(growthData) {
    if (!growthData) return;
    if (growthData.semesters) {
      this.renderSemesterSgpaLine('chart-growth-line', growthData.semesters, growthData.avg_cgpa);
      this.renderSemesterDisciplineBar('chart-subject-growth', growthData.semesters);
    } else {
      this.renderGrowthLine('chart-growth-line', growthData.timeline);
      this.renderSubjectGrowthBar('chart-subject-growth', growthData.subject_growth);
    }
  }

  renderSemesterSgpaLine(canvasId, semesters, avgCgpa = 0) {
    const ctx = document.getElementById(canvasId);
    if (!ctx || !semesters) return;

    if (this.growthLineChart) {
      this.growthLineChart.destroy();
    }

    const labels = semesters.map(s => `Sem ${s.semester_num}`);
    const sgpas = semesters.map(s => s.sgpa);
    const pointColors = semesters.map(s => {
      if (s.backlogs_count > 0 || s.sgpa < 6.0) return '#ef4444'; // Red
      if (s.sgpa < 7.0) return '#f59e0b'; // Yellow
      return '#10b981'; // Green
    });

    this.growthLineChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels,
        datasets: [
          {
            label: 'Semester SGPA (0 - 10.0)',
            data: sgpas,
            borderColor: '#4f46e5',
            backgroundColor: 'rgba(79, 70, 229, 0.12)',
            fill: true,
            tension: 0.35,
            borderWidth: 3,
            pointBackgroundColor: pointColors,
            pointBorderColor: '#ffffff',
            pointBorderWidth: 2,
            pointRadius: 7,
            pointHoverRadius: 10,
          },
          {
            label: `Cumulative Avg CGPA (${avgCgpa})`,
            data: labels.map(() => avgCgpa),
            borderColor: '#0284c7',
            borderDash: [5, 5],
            borderWidth: 2,
            pointRadius: 0,
            fill: false,
          },
          {
            label: 'Placement Green Benchmark (7.0)',
            data: labels.map(() => 7.0),
            borderColor: 'rgba(16, 185, 129, 0.75)',
            borderDash: [3, 3],
            borderWidth: 1.5,
            pointRadius: 0,
            fill: false,
          },
          {
            label: 'Minimum Cutoff Caution (6.0)',
            data: labels.map(() => 6.0),
            borderColor: 'rgba(239, 68, 68, 0.75)',
            borderDash: [3, 3],
            borderWidth: 1.5,
            pointRadius: 0,
            fill: false,
          }
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            min: 4.0,
            max: 10.0,
            grid: { color: 'rgba(0, 0, 0, 0.06)' },
            ticks: {
              color: '#64748b',
              stepSize: 1.0,
              callback: val => `${val}.0`
            },
            title: {
              display: true,
              text: 'Semester Grade Point Average (SGPA)',
              color: '#475569',
              font: { weight: '600' }
            }
          },
          x: {
            grid: { display: false },
            ticks: { color: '#475569', font: { weight: '600' } }
          }
        },
        plugins: {
          tooltip: {
            callbacks: {
              afterLabel: (ctx) => {
                if (ctx.datasetIndex === 0) {
                  const item = semesters[ctx.dataIndex];
                  const statusStr = item.backlogs_count > 0 ? `⚠️ ${item.backlogs_count} Backlog(s)` : '✅ Cleared';
                  return `SGPA: ${item.sgpa}/10.0 · Credits: ${item.credits_earned}/${item.credits_total} · ${statusStr}`;
                }
                return '';
              }
            }
          },
          legend: {
            position: 'top',
            labels: { color: '#334155', font: { weight: '600', size: 11 } }
          }
        }
      }
    });
  }

  renderSemesterDisciplineBar(canvasId, semesters) {
    const ctx = document.getElementById(canvasId);
    if (!ctx || !semesters) return;

    if (this.subjectGrowthBarChart) {
      this.subjectGrowthBarChart.destroy();
    }

    // Average marks across early vs late semesters
    const sem1_4 = semesters.slice(0, 4);
    const sem5_8 = semesters.slice(4, 8);

    const calcAvgMarks = (semList) => {
      let sum = 0, count = 0;
      semList.forEach(s => s.subjects.forEach(sub => { sum += sub.marks; count++; }));
      return count > 0 ? Math.round((sum / count) * 10) / 10 : 0;
    };

    const avgEarly = calcAvgMarks(sem1_4);
    const avgLate = calcAvgMarks(sem5_8);
    const overallAvg = calcAvgMarks(semesters);

    this.subjectGrowthBarChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: ['Foundation Years (Sem 1-4)', 'Advanced Tech & Capstone (Sem 5-8)', '8-Semester Program Aggregate'],
        datasets: [
          {
            label: 'Average Score (%)',
            data: [avgEarly, avgLate, overallAvg],
            backgroundColor: ['rgba(148, 163, 184, 0.75)', 'rgba(79, 70, 229, 0.85)', 'rgba(16, 185, 129, 0.85)'],
            borderRadius: 8,
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: false,
            min: 50,
            max: 100,
            grid: { color: 'rgba(0, 0, 0, 0.06)' },
            ticks: { color: '#64748b', callback: val => `${val}%` }
          },
          x: {
            grid: { display: false },
            ticks: { color: '#475569', font: { weight: '600' } }
          }
        },
        plugins: {
          legend: { display: false }
        }
      }
    });
  }

  renderGrowthLine(canvasId, timeline) {
    const ctx = document.getElementById(canvasId);
    if (!ctx || !timeline) return;

    if (this.growthLineChart) {
      this.growthLineChart.destroy();
    }

    const labels = timeline.map(t => t.term_name.split('·')[0].trim());
    const scores = timeline.map(t => t.percentage);

    this.growthLineChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels,
        datasets: [
          {
            label: 'Academic Growth Curve (% Score)',
            data: scores,
            borderColor: '#4f46e5',
            backgroundColor: 'rgba(79, 70, 229, 0.12)',
            fill: true,
            tension: 0.35,
            borderWidth: 3,
            pointBackgroundColor: '#4f46e5',
            pointBorderColor: '#ffffff',
            pointBorderWidth: 2,
            pointRadius: 6,
            pointHoverRadius: 9,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            min: 50,
            max: 100,
            grid: { color: 'rgba(0, 0, 0, 0.06)' },
            ticks: {
              color: '#64748b',
              callback: val => `${val}%`
            },
            title: {
              display: true,
              text: 'Aggregate Score (%)',
              color: '#475569',
              font: { weight: '600' }
            }
          },
          x: {
            grid: { display: false },
            ticks: { color: '#475569', font: { weight: '600' } }
          }
        },
        plugins: {
          tooltip: {
            callbacks: {
              afterLabel: (ctx) => {
                const item = timeline[ctx.dataIndex];
                return `GPA: ${item.gpa} · Grade: ${item.grade} (${item.date_label})`;
              }
            }
          },
          legend: {
            position: 'top',
            labels: { color: '#334155', font: { weight: '600' } }
          }
        }
      }
    });
  }

  renderSubjectGrowthBar(canvasId, subjectGrowths) {
    const ctx = document.getElementById(canvasId);
    if (!ctx || !subjectGrowths) return;

    if (this.subjectGrowthBarChart) {
      this.subjectGrowthBarChart.destroy();
    }

    const labels = subjectGrowths.map(s => s.subject);
    const baselines = subjectGrowths.map(s => s.baseline_score);
    const currents = subjectGrowths.map(s => s.current_score);

    this.subjectGrowthBarChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels,
        datasets: [
          {
            label: 'Baseline (Term 1)',
            data: baselines,
            backgroundColor: 'rgba(148, 163, 184, 0.65)',
            borderRadius: 6,
          },
          {
            label: 'Current Evaluation',
            data: currents,
            backgroundColor: 'rgba(79, 70, 229, 0.85)',
            borderRadius: 6,
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            max: 100,
            grid: { color: 'rgba(0, 0, 0, 0.06)' },
            ticks: { color: '#64748b' }
          },
          x: {
            grid: { display: false },
            ticks: { color: '#475569', font: { weight: '600' } }
          }
        },
        plugins: {
          legend: {
            position: 'top',
            labels: { color: '#334155', font: { weight: '600' } }
          }
        }
      }
    });
  }

  renderCohortCharts(cohortData) {
    if (!cohortData) return;
    this.renderRiskDonut('chart-risk-donut', cohortData.risk_distribution);
    this.renderScatter('chart-correlation-scatter', cohortData.correlation_scatter);
    this.renderSubjectBar('chart-subject-bar', cohortData.subject_averages);
  }

  renderRiskDonut(canvasId, riskDist) {
    const ctx = document.getElementById(canvasId);
    if (!ctx || !riskDist) return;

    if (this.riskDonutChart) {
      this.riskDonutChart.destroy();
    }

    const labels = Object.keys(riskDist);
    const data = Object.values(riskDist);

    const colors = {
      'Critical Intervention': '#ef4444',
      'Moderate Risk': '#f59e0b',
      'On Track': '#10b981',
      'High Achiever': '#6366f1',
    };

    const bgColors = labels.map((l) => colors[l] || '#94a3b8');

    this.riskDonutChart = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels,
        datasets: [
          {
            data,
            backgroundColor: bgColors,
            borderColor: '#ffffff',
            borderWidth: 3,
            hoverOffset: 6,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '68%',
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              boxWidth: 12,
              padding: 12,
              color: '#334155',
              font: { weight: '500' },
            },
          },
        },
      },
    });
  }

  renderScatter(canvasId, points) {
    const ctx = document.getElementById(canvasId);
    if (!ctx || !points) return;

    if (this.scatterChart) {
      this.scatterChart.destroy();
    }

    const scatterData = points.map((p) => ({
      x: p.x,
      y: p.y,
      name: p.name,
      score: p.score,
      risk: p.risk,
    }));

    this.scatterChart = new Chart(ctx, {
      type: 'scatter',
      data: {
        datasets: [
          {
            label: 'Students (Study Hrs vs Exam)',
            data: scatterData,
            backgroundColor: (context) => {
              const raw = context.raw;
              if (!raw) return '#6366f1';
              if (raw.risk === 'Critical Intervention') return '#ef4444';
              if (raw.risk === 'Moderate Risk') return '#f59e0b';
              if (raw.risk === 'High Achiever') return '#818cf8';
              return '#10b981';
            },
            pointRadius: 6,
            pointHoverRadius: 9,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            title: {
              display: true,
              text: 'Weekly Study Hours (h)',
              color: '#475569',
              font: { weight: '600' },
            },
            grid: { color: 'rgba(0, 0, 0, 0.06)' },
            ticks: { color: '#64748b' },
          },
          y: {
            title: {
              display: true,
              text: 'Exam Score (%)',
              color: '#475569',
              font: { weight: '600' },
            },
            min: 30,
            max: 100,
            grid: { color: 'rgba(0, 0, 0, 0.06)' },
            ticks: { color: '#64748b' },
          },
        },
        plugins: {
          tooltip: {
            callbacks: {
              label: (context) => {
                const item = context.raw;
                return `${item.name}: ${item.x} hrs study, ${item.y}% exam (Score: ${item.score})`;
              },
            },
          },
          legend: { display: false },
        },
      },
    });
  }

  renderSubjectBar(canvasId, subjectAverages) {
    const ctx = document.getElementById(canvasId);
    if (!ctx || !subjectAverages) return;

    if (this.subjectBarChart) {
      this.subjectBarChart.destroy();
    }

    const labels = Object.keys(subjectAverages);
    const values = Object.values(subjectAverages);

    this.subjectBarChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels,
        datasets: [
          {
            label: 'Average Score (%)',
            data: values,
            backgroundColor: [
              'rgba(99, 102, 241, 0.85)',
              'rgba(14, 165, 233, 0.85)',
              'rgba(16, 185, 129, 0.85)',
              'rgba(245, 158, 11, 0.85)',
            ],
            borderRadius: 6,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            max: 100,
            grid: { color: 'rgba(0, 0, 0, 0.06)' },
            ticks: { color: '#64748b' },
          },
          x: {
            grid: { display: false },
            ticks: { color: '#475569', font: { weight: '500' } },
          },
        },
        plugins: {
          legend: { display: false },
        },
      },
    });
  }
}

window.perfCharts = new PerformanceCharts();
