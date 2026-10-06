async function getJSON(url, options={}) {
  const r = await fetch(url, options);
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

function bandClass(band) {
  return band.toLowerCase();
}

function escapeHTML(value) {
  return String(value).replace(/[&<>"']/g, character => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;'
  })[character]);
}

function openRecordDialog(id) {
  document.getElementById(id).showModal();
}

function closeRecordDialog(id) {
  document.getElementById(id).close();
}

function responseMessage(error) {
  try {
    const response = JSON.parse(error.message);
    if (typeof response.detail === 'string') return response.detail;
  } catch {}
  return 'Unable to save this record. Check the entered values and try again.';
}

async function loadSummary() {
  const s = await getJSON('/api/dashboard/summary');
  document.getElementById('summary').innerHTML = `
    <div class="metric"><span>Total students</span><b>${s.total_students}</b></div>
    <div class="metric"><span>High / Critical</span><b>${s.high_risk}</b></div>
    <div class="metric"><span>Critical</span><b>${s.critical}</b></div>
    <div class="metric"><span>Avg engagement</span><b>${s.average_engagement}%</b></div>`;
}

async function loadStudents() {
  const data = await getJSON('/api/students');
  const rows = [];
  for (const s of data.slice(0, 30)) {
    const p = await getJSON(`/api/students/${s.id}/prediction`);
    rows.push(`<tr>
      <td><b>${escapeHTML(s.id)}</b><br>${escapeHTML(s.name)}</td><td>${escapeHTML(s.department)}</td>
      <td>${s.attendance_pct}%</td><td>${s.avg_exam_score}</td>
      <td><span class="risk ${bandClass(p.risk_band)}">${p.risk_band}</span></td>
      <td>${(p.risk_probability*100).toFixed(1)}%</td>
      <td>${p.engagement_score}%</td>
    </tr>`);
  }
  document.getElementById('students').innerHTML = `<table><thead><tr><th>Student</th><th>Dept</th><th>Attendance</th><th>Exam</th><th>Risk</th><th>Probability</th><th>Engagement</th></tr></thead><tbody>${rows.join('')}</tbody></table>`;
}

async function facultyLoad(risk) {
  const data = await getJSON('/api/students' + (risk ? `?risk=${risk}` : ''));
  const rows = [];
  for (const s of data) {
    const p = await getJSON(`/api/students/${s.id}/prediction`);
    rows.push(`<tr><td>${escapeHTML(s.id)}<br>${escapeHTML(s.name)}</td><td>${escapeHTML(s.department)}</td><td>${s.attendance_pct}%</td><td>${s.assignment_completion_pct}%</td><td>${p.engagement_score}%</td><td><span class="risk ${bandClass(p.risk_band)}">${escapeHTML(p.risk_band)}</span></td><td><button onclick="createPlan('${escapeHTML(s.id)}')">Plan</button></td></tr>`);
  }
  document.getElementById('faculty-table').innerHTML = `<table><thead><tr><th>Student</th><th>Dept</th><th>Attendance</th><th>Assignments</th><th>Engagement</th><th>Risk</th><th>Action</th></tr></thead><tbody>${rows.join('')}</tbody></table>`;
}

async function loadTeachers() {
  const data = await getJSON('/api/teachers');
  const target = document.getElementById('teachers-table');
  if (!data.length) {
    target.innerHTML = '<p class="empty-state">No teachers added yet.</p>';
    return;
  }
  target.innerHTML = `<table><thead><tr><th>Faculty ID</th><th>Name</th><th>Email</th><th>Department</th></tr></thead><tbody>${data.map(teacher => `<tr><td>${escapeHTML(teacher.id)}</td><td>${escapeHTML(teacher.name)}</td><td>${escapeHTML(teacher.email)}</td><td>${escapeHTML(teacher.department)}</td></tr>`).join('')}</tbody></table>`;
}

async function submitStudentForm(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const button = form.querySelector('[type="submit"]');
  const status = document.getElementById('student-form-status');
  const payload = Object.fromEntries(new FormData(form));
  for (const input of form.querySelectorAll('input[type="number"]')) {
    payload[input.name] = Number(input.value);
  }
  button.disabled = true;
  status.textContent = '';
  try {
    const student = await getJSON('/api/students', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(payload)
    });
    form.reset();
    closeRecordDialog('student-dialog');
    document.getElementById('directory-status').textContent = `Student ${student.id} added.`;
    await facultyLoad('');
  } catch (error) {
    status.textContent = responseMessage(error);
  } finally {
    button.disabled = false;
  }
}

async function submitTeacherForm(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const button = form.querySelector('[type="submit"]');
  const status = document.getElementById('teacher-form-status');
  const payload = Object.fromEntries(new FormData(form));
  button.disabled = true;
  status.textContent = '';
  try {
    const teacher = await getJSON('/api/teachers', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(payload)
    });
    form.reset();
    closeRecordDialog('teacher-dialog');
    document.getElementById('directory-status').textContent = `Teacher ${teacher.name} added.`;
    await loadTeachers();
  } catch (error) {
    status.textContent = responseMessage(error);
  } finally {
    button.disabled = false;
  }
}

async function createPlan(id) {
  const p = await getJSON(`/api/students/${id}/intervention`, {method:'POST'});
  alert(p.actions.map(x => `${x.priority}: ${x.action}`).join('\n'));
  loadInterventions();
}

async function loadInterventions() {
  const data = await getJSON('/api/interventions');
  document.getElementById('interventions').innerHTML = data.length ? `<table><thead><tr><th>Student</th><th>Priority</th><th>Action</th><th>Reason</th></tr></thead><tbody>${data.map(x => `<tr><td>${x.student_id}</td><td>${x.priority}</td><td>${x.action}</td><td>${x.reason}</td></tr>`).join('')}</tbody></table>` : '<p>No intervention actions generated yet.</p>';
}

async function studentView() {
  const id = document.getElementById('student-id').value.trim();
  if (!id) return;
  try {
    const s = await getJSON(`/api/students/${id}`);
    const p = await getJSON(`/api/students/${id}/prediction`);
    document.getElementById('student-report').innerHTML = `
      <section class="hero">
        <div><span class="pill">${s.department} · Semester ${s.semester}</span><h2>${s.name}</h2><p>Personalized early-warning report for ${s.id}.</p></div>
        <div class="score"><span>Dropout risk</span><b>${(p.risk_probability*100).toFixed(1)}%</b><strong class="risk ${bandClass(p.risk_band)}">${p.risk_band}</strong></div>
      </section>
      <section class="cards"><div class="metric"><span>Engagement score</span><b>${p.engagement_score}%</b></div><div class="metric"><span>Attendance</span><b>${s.attendance_pct}%</b></div><div class="metric"><span>Assignments</span><b>${s.assignment_completion_pct}%</b></div><div class="metric"><span>Exam average</span><b>${s.avg_exam_score}</b></div></section>
      <section class="panel"><h3>What is influencing the result?</h3><div class="factors">${p.top_factors.map(f => `<div class="factor"><b>${f.feature}</b><span class="${f.impact==='Risk increasing'?'danger':'safe'}">${f.impact}</span></div>`).join('')}</div></section>
      <section class="panel"><h3>Recommended next steps</h3><button onclick="studentPlan('${id}')">Generate my support plan</button><div id="plan"></div></section>`;
  } catch(e) {
    document.getElementById('student-report').innerHTML = `<section class="panel"><b>Student not found.</b> Try STU1001–STU1080.</section>`;
  }
}

async function studentPlan(id) {
  const p = await getJSON(`/api/students/${id}/intervention`, {method:'POST'});
  document.getElementById('plan').innerHTML = p.actions.map(x => `<div class="recommendation"><b>${x.action}</b><p>${x.reason}</p></div>`).join('');
}
