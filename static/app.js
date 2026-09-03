const elements = {
  day: document.querySelector('#day-picker'), body: document.querySelector('#ledger-body'), empty: document.querySelector('#ledger-empty'),
  total: document.querySelector('#total-time'), focus: document.querySelector('#focus-time'), plans: document.querySelector('#plan-count'),
  planList: document.querySelector('#plan-list'), planEmpty: document.querySelector('#plan-empty'), energy: document.querySelector('#energy-bars'),
  entryOverlay: document.querySelector('#entry-overlay'), planOverlay: document.querySelector('#plan-overlay'), entryForm: document.querySelector('#entry-form'), planForm: document.querySelector('#plan-form'),
  timer: document.querySelector('#timer-toggle'), timerCopy: document.querySelector('#timer-copy'),
};
let timerStart = null;

function localDate() { return new Date().toLocaleDateString('en-CA'); }
function toLocalInput(date) { return new Date(date.getTime() - date.getTimezoneOffset() * 60000).toISOString().slice(0, 16); }
function minutes(value) { const hour = Math.floor(value / 60); const rest = value % 60; return hour ? `${hour}小时${rest ? `${rest}分` : ''}` : `${rest}分钟`; }
function escapeText(value) { const holder = document.createElement('span'); holder.textContent = value; return holder.innerHTML; }
function showOverlay(overlay) { overlay.showModal(); overlay.querySelector('input:not([type="hidden"])')?.focus(); }
function hideOverlays() { document.querySelectorAll('.overlay').forEach((overlay) => { if (overlay.open) overlay.close(); }); }

function render(summary) {
  elements.total.innerHTML = `${summary.total_minutes} <small>分钟</small>`;
  elements.focus.innerHTML = `${summary.focus_minutes} <small>分钟</small>`;
  elements.plans.innerHTML = `${summary.plans.length} <small>项</small>`;
  elements.empty.hidden = summary.entries.length !== 0;
  elements.body.innerHTML = summary.entries.map((entry) => `<tr><td>${entry.started_at.slice(11,16)}–${entry.ended_at.slice(11,16)}</td><td><strong>${escapeText(entry.title)}</strong>${entry.note ? `<br><span class="muted">${escapeText(entry.note)}</span>` : ''}</td><td>${escapeText(entry.category)}</td><td><span class="tag ${entry.bs_mode.toLowerCase()}">${entry.bs_mode}</span></td><td>${entry.energy} / 5</td><td>${minutes(entry.minutes)}</td></tr>`).join('');
  elements.planEmpty.hidden = summary.plans.length !== 0;
  elements.planList.innerHTML = summary.plans.map((plan) => `<article class="plan-item"><strong>${escapeText(plan.title)}</strong><span class="tag">${escapeText(plan.category)}</span><p>${plan.target_minutes} 分钟配额</p></article>`).join('');
  const byMode = summary.entries.reduce((value, entry) => ({ ...value, [entry.bs_mode]: value[entry.bs_mode] + entry.minutes }), { B: 0, S: 0 });
  const total = Math.max(byMode.B + byMode.S, 1);
  elements.energy.innerHTML = [['B','moss',byMode.B],['S','social',byMode.S]].map(([label, style, value]) => `<div class="energy-row"><strong>${label}</strong><div class="bar ${style}"><span style="width:${Math.round(value / total * 100)}%"></span></div><span>${value}m</span></div>`).join('');
}

async function load() {
  try { const response = await fetch(`/api/summary?date=${elements.day.value}`); if (!response.ok) throw new Error('读取失败'); render(await response.json()); }
  catch { elements.body.innerHTML = ''; elements.empty.hidden = false; elements.empty.innerHTML = '<strong>暂时无法读取时间账本</strong><span>请检查服务连接后重试。</span>'; }
}
async function submit(url, form, errorTarget) {
  const raw = Object.fromEntries(new FormData(form));
  const payload = { ...raw, energy: Number(raw.energy), target_minutes: Number(raw.target_minutes) };
  const button = form.querySelector('button[type="submit"]'); const label = button.textContent; button.disabled = true; button.textContent = '保存中…';
  try { const response = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) }); const result = await response.json(); if (!response.ok) { errorTarget.textContent = result.error; return; } hideOverlays(); form.reset(); await load(); }
  catch { errorTarget.textContent = '暂时无法保存，请检查服务连接。'; }
  finally { button.disabled = false; button.textContent = label; }
}

elements.day.value = localDate();
elements.day.addEventListener('change', load);
document.querySelector('#new-entry').addEventListener('click', () => { const now = new Date(); elements.entryForm.started_at.value = toLocalInput(now); elements.entryForm.ended_at.value = toLocalInput(new Date(now.getTime() + 30 * 60000)); showOverlay(elements.entryOverlay); });
document.querySelector('#new-plan').addEventListener('click', () => showOverlay(elements.planOverlay));
document.querySelectorAll('[data-close],.overlay').forEach((node) => node.addEventListener('click', (event) => { if (event.target === node || event.target.matches('[data-close]')) hideOverlays(); }));
elements.entryForm.addEventListener('submit', (event) => { event.preventDefault(); submit('/api/entries', elements.entryForm, document.querySelector('#entry-error')); });
elements.planForm.addEventListener('submit', (event) => { event.preventDefault(); elements.planForm.planned_date.value = elements.day.value; submit('/api/plans', elements.planForm, document.querySelector('#plan-error')); });
elements.timer.addEventListener('click', () => { if (!timerStart) { timerStart = new Date(); elements.timer.textContent = '结束并保存'; elements.timerCopy.textContent = `已从 ${timerStart.toLocaleTimeString('zh-CN', {hour:'2-digit',minute:'2-digit'})} 开始记录。`; return; } elements.entryForm.started_at.value = toLocalInput(timerStart); elements.entryForm.ended_at.value = toLocalInput(new Date()); elements.timer.textContent = '开始专注记录'; elements.timerCopy.textContent = '开始后，结束时补充分类和能量即可。'; timerStart = null; showOverlay(elements.entryOverlay); });
if ('serviceWorker' in navigator) navigator.serviceWorker.register('/sw.js');
load();
