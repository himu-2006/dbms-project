// robust main.js for ExamSeater UI
// Logs API state and tolerantly maps different field names (roll_no / roll etc.)

async function fetchJson(path, opts) {
  const res = await fetch(path, opts);
  const txt = await res.text();
  try { return { ok: res.ok, status: res.status, json: JSON.parse(txt) }; }
  catch(e) { return { ok: res.ok, status: res.status, json: txt }; }
}

function idOf(obj, ...candidates) {
  for (const k of candidates) if (obj && obj[k] !== undefined) return obj[k];
  return undefined;
}

function safeStr(v){ if(v===null||v===undefined) return ''; return String(v); }

async function loadState(){
  const r = await fetchJson('/api/state');
  window.STATE = r.json || {};
  console.log("STATE from /api/state:", window.STATE);
  // normalise regs to numeric keys if possible
  const regs = {};
  const rawRegs = window.STATE.regs || {};
  try {
    // rawRegs might be {"1":[1,2]} or {1:[1,2]} or {"E2001":["S3001"...]}
    Object.keys(rawRegs).forEach(k=>{
      // try numeric conversion
      const n = Number(k);
      const key = (isNaN(n) ? k : n);
      regs[key] = rawRegs[k];
    });
  } catch(e){ console.warn('regs normalise failed', e); }
  window.STATE.regs_norm = regs;
}

function getExamId(ex){
  return idOf(ex, 'exam_id', 'id', 'examId');
}
function getStudentId(s){
  return idOf(s, 'student_id', 'id', 'studentId');
}
function getStudentRoll(s){
  return idOf(s, 'roll_no', 'roll', 'rollNo') || '';
}
function getStudentName(s){
  return idOf(s, 'name', 'full_name') || '';
}

async function renderAll(){
  await loadState();

  // stats
  const examsCount = Array.isArray(STATE.exams) ? STATE.exams.length : 0;
  const studentsCount = Array.isArray(STATE.students) ? STATE.students.length : 0;
  const roomsCount = Array.isArray(STATE.rooms) ? STATE.rooms.length : 0;
  const statExams = document.getElementById('statExams');
  if(statExams) statExams.innerText = examsCount;
  const statStudents = document.getElementById('statStudents');
  if(statStudents) statStudents.innerText = studentsCount;
  const statRooms = document.getElementById('statRooms');
  if(statRooms) statRooms.innerText = roomsCount;

  // upcoming preview
  const preview = document.getElementById('examPreview');
  if(preview){
    const up = (STATE.exams && STATE.exams[0]) || null;
    preview.innerHTML = up ? `<strong>${safeStr(up.course_code||up.course)}</strong> — ${safeStr(up.exam_date||up.date)} ${safeStr(up.start_time||'')} to ${safeStr(up.end_time||'')}` : '—';
  }

  // Exams table
  const examsT = document.querySelector('#examsTable tbody');
  if(examsT){
    examsT.innerHTML = '';
    (STATE.exams || []).forEach(ex=>{
      const eid = getExamId(ex);
      // regs lookup tolerant: numeric or string key
      const regsList = STATE.regs_norm[eid] || STATE.regs_norm[String(eid)] || [];
      const regsCount = Array.isArray(regsList) ? regsList.length : 0;
      const tr = document.createElement('tr');
      tr.innerHTML = `<td>${safeStr(ex.course_code || ex.course || ex.courseCode)}</td>
                      <td>${safeStr(ex.exam_date)}</td>
                      <td>${safeStr(ex.start_time||'')} - ${safeStr(ex.end_time||'')}</td>
                      <td>${regsCount}</td>
                      <td><button class="btn ghost" data-action="reg" data-id="${eid}">Register All</button></td>`;
      examsT.appendChild(tr);
    });

    // exam select for assign
    const sel = document.getElementById('selectExam');
    if(sel){
      sel.innerHTML = '';
      (STATE.exams || []).forEach(ex=>{
        const eid = getExamId(ex);
        const opt = document.createElement('option');
        opt.value = eid;
        opt.text = `${safeStr(ex.course_code||ex.course)} — ${safeStr(ex.exam_date)}`;
        sel.appendChild(opt);
      });
    }
  }

  // rooms list
  const roomsList = document.getElementById('roomsList');
  if(roomsList){
    roomsList.innerHTML = '';
    (STATE.rooms || []).forEach(r=>{
      const d = document.createElement('div'); d.className='room';
      d.innerHTML = `<strong>${safeStr(r.room_code)}</strong>
                     <div class="muted">Cap: ${safeStr(r.capacity)}</div>
                     <div class="muted">${safeStr(r.building||'')} Floor:${safeStr(r.floor||'')}</div>`;
      roomsList.appendChild(d);
    });
  }

  // students table
  const studT = document.querySelector('#studentsTable tbody');
  if(studT){
    studT.innerHTML = '';
    (STATE.students || []).forEach(s=>{
      const sid = getStudentId(s);
      const tr = document.createElement('tr');
      tr.innerHTML = `<td>${safeStr(getStudentRoll(s))}</td>
                      <td>${safeStr(getStudentName(s))}</td>
                      <td>${safeStr(s.department||'')}</td>
                      <td><button class="btn ghost" data-action="del-stud" data-id="${sid}">Del</button></td>`;
      studT.appendChild(tr);
    });
  }

  // invigilators table
  const invT = document.querySelector('#invTable tbody');
  if(invT){
    invT.innerHTML = '';
    (STATE.invigilators || []).forEach(i=>{
      const iid = idOf(i, 'invigilator_id', 'id');
      const tr = document.createElement('tr');
      tr.innerHTML = `<td>${safeStr(i.name)}</td><td>${safeStr(i.employee_no||i.emp||'')}</td><td><button class="btn ghost" data-action="del-inv" data-id="${iid}">Del</button></td>`;
      invT.appendChild(tr);
    });
  }
}

// clicks & form wiring (keeps behavior same)
document.addEventListener('click', async (e)=>{
  const t = e.target;
  if(!t) return;
  if(t.id==='exportJSON'){ window.location = '/api/export'; }
  if(t.dataset.action==='reg'){ const id = t.dataset.id; await fetch('/api/register_all',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({exam_id:id})}); await renderAll(); alert('registered'); }
  if(t.dataset.action==='del-stud'){ const id=t.dataset.id; await fetch('/api/students/'+id,{method:'DELETE'}); await renderAll(); }
  if(t.dataset.action==='del-inv'){ const id=t.dataset.id; await fetch('/api/invigilators/'+id,{method:'DELETE'}); await renderAll(); }
});

document.addEventListener('DOMContentLoaded', async ()=>{
  await renderAll();

  // add room
  document.getElementById('addRoom')?.addEventListener('click', async ()=>{
    const code = document.getElementById('roomCode').value.trim();
    const cap = document.getElementById('roomCap').value;
    const building = document.getElementById('roomBuilding')?.value || '';
    const floor = document.getElementById('roomFloor')?.value || '';
    if(!code||!cap) return alert('fill both');
    await fetch('/api/rooms',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({room_code:code,capacity:cap,building:building,floor:floor})});
    document.getElementById('roomCode').value=''; document.getElementById('roomCap').value=''; if(document.getElementById('roomBuilding')) document.getElementById('roomBuilding').value=''; if(document.getElementById('roomFloor')) document.getElementById('roomFloor').value='';
    await renderAll();
  });

  // add exam
  document.getElementById('addExam')?.addEventListener('click', async ()=>{
    const c = document.getElementById('examCourse').value.trim();
    const d = document.getElementById('examDate').value;
    const s = document.getElementById('examStart').value;
    const e = document.getElementById('examEnd').value;
    if(!c||!d||!s||!e) return alert('fill all');
    const resp = await fetch('/api/exams',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({course_code:c,course_title:c,exam_date:d,start_time:s,end_time:e})});
    const j = await resp.json().catch(()=>({}));
    if(!resp.ok) return alert('Error adding exam: '+(j.error||JSON.stringify(j)));
    document.getElementById('examCourse').value=''; document.getElementById('examDate').value=''; document.getElementById('examStart').value=''; document.getElementById('examEnd').value='';
    await renderAll();
  });

  // add student
  document.getElementById('addStudent')?.addEventListener('click', async ()=>{
    const r = document.getElementById('studRoll').value.trim();
    const n = document.getElementById('studName').value.trim();
    const d = document.getElementById('studDept').value.trim();
    const y = document.getElementById('studYear')?.value || null;
    if(!r||!n) return alert('roll & name');
    await fetch('/api/students',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({roll:r,name:n,dept:d,year:y})});
    document.getElementById('studRoll').value=''; document.getElementById('studName').value=''; document.getElementById('studDept').value=''; if(document.getElementById('studYear')) document.getElementById('studYear').value='';
    await renderAll();
  });

  // add invigilator
  document.getElementById('addInv')?.addEventListener('click', async ()=>{
    const n = document.getElementById('invName').value.trim();
    const e = document.getElementById('invEmp').value.trim();
    const d = document.getElementById('invDept').value.trim();
    if(!n) return alert('name');
    await fetch('/api/invigilators',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:n,emp:e,dept:d})});
    document.getElementById('invName').value=''; document.getElementById('invEmp').value=''; document.getElementById('invDept').value='';
    await renderAll();
  });

  // assign seats
  document.getElementById('assignSeatsBtn')?.addEventListener('click', async ()=>{
    const examId = document.getElementById('selectExam').value;
    if(!examId) return alert('pick exam');
    const res = await fetch('/api/assign/'+examId,{method:'POST'});
    const j = await res.json().catch(()=>({}));
    if(j.error) return alert(j.error);
    if(j.warning) alert(j.warning);
    // render assignments by room
    const out = document.getElementById('assignResult');
    out.innerHTML = '';
    const assignments = j.assignments || {};
    const rooms = (STATE.rooms || []).slice().sort((a,b)=>b.capacity - a.capacity);
    rooms.forEach(r => {
      const list = assignments[r.room_id] || assignments[String(r.room_id)] || [];
      const box = document.createElement('div'); box.className='card';
      let html = `<h4>${r.room_code} — Seats: ${list.length}/${r.capacity}</h4><div class="small">`;
      list.forEach(a => html += `<span class="seat taken">${a.seat}</span> `);
      html += `</div><div><table class="table"><thead><tr><th>Seat</th><th>Roll</th><th>Name</th></tr></thead><tbody>`;
      list.forEach(a => html += `<tr><td>${a.seat}</td><td>${a.student?.roll_no||a.student?.roll||''}</td><td>${a.student?.name||''}</td></tr>`);
      html += `</tbody></table></div>`;
      box.innerHTML = html;
      out.appendChild(box);
    });
  });

  // clear seats
  document.getElementById('clearSeats')?.addEventListener('click', async ()=>{
    await fetch('/api/clear_assign',{method:'POST'});
    document.getElementById('assignResult').innerHTML='';
    await renderAll();
  });
});
