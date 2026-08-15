import { fetchJson, money, escapeHtml } from './api.js';
import { initializeMap, renderProjects } from './map.js';

const state = { projects: [], filtered: [], summary: null, radar: null };
const $ = (id) => document.getElementById(id);

function number(value) { return Number(value || 0).toLocaleString(); }
function unique(values) { return [...new Set(values.filter(Boolean).map(v => String(v).trim()))].sort((a,b) => a.localeCompare(b)); }
function optionList(select, values) { for (const value of values) { const o=document.createElement('option'); o.value=value; o.textContent=value; select.appendChild(o); } }
function statusText(text) { const v=String(text || 'Unknown'); return v.length > 80 ? `${v.slice(0,77)}...` : v; }

function renderKpis() {
  const s = state.summary;
  if (!s) return;
  $('kpiStrip').innerHTML = [
    ['PROJECTS', number(s.project_count)],
    ['GEOCODED', number(s.geocoded_count)],
    ['DISCLOSED VALUE', money(s.disclosed_budget_total)],
    ['BUDGETS DISCLOSED', number(s.budget_disclosure_count)],
  ].map(([label,value]) => `<div class="kpi-card"><span>${label}</span><strong>${value}</strong></div>`).join('');
}

function detail(project) {
  const c = project.complexity || { score: 0, band: 'unknown', reasons: [] };
  $('projectDetail').innerHTML = `
    <div class="eyebrow">PROJECT DETAIL</div>
    <div class="detail-status">${escapeHtml(statusText(project.status))}</div>
    <h2>${escapeHtml(project.project || 'Infrastructure project')}</h2>
    <p class="subtle">${escapeHtml(project.description || project.result || 'No project description published.')}</p>
    <div class="detail-grid">
      <div class="detail-metric"><span>Community</span><strong>${escapeHtml(project.community || project.area || 'Not specified')}</strong></div>
      <div class="detail-metric"><span>Category</span><strong>${escapeHtml(project.category || 'Not specified')}</strong></div>
      <div class="detail-metric"><span>Disclosed budget</span><strong>${money(project.budget)}</strong></div>
      <div class="detail-metric"><span>Target completion</span><strong>${escapeHtml(project.target_completion || 'Not disclosed')}</strong></div>
      <div class="detail-metric"><span>Region</span><strong>${escapeHtml(project.region || 'Not specified')}</strong></div>
      <div class="detail-metric"><span>Ministry</span><strong>${escapeHtml(project.supporting_ministry || 'Not specified')}</strong></div>
    </div>
    <div class="eyebrow">PLANNING COMPLEXITY</div>
    <div class="compact-stat"><span>Screening score</span><strong>${c.score}/100 - ${escapeHtml(c.band)}</strong></div>
    <div class="complexity-meter"><i style="width:${c.score}%"></i></div>
    <ul class="reason-list">${(c.reasons || []).map(r => `<li>${escapeHtml(r)}</li>`).join('')}</ul>
    <div class="rail-divider"></div>
    ${project.website ? `<a class="source-link" href="${escapeHtml(project.website)}" target="_blank" rel="noreferrer">Open official project page</a>` : '<span class="subtle">No project-specific source link published.</span>'}
  `;
}

function applyFilters() {
  const category=$('categoryFilter').value, status=$('statusFilter').value, region=$('regionFilter').value, minBudget=Number($('budgetFilter').value || 0);
  state.filtered = state.projects.filter(p => (!category || p.category===category) && (!status || p.status===status) && (!region || p.region===region) && Number(p.budget || 0)>=minBudget);
  $('visibleCount').textContent = number(state.filtered.length);
  renderProjects(state.filtered);
}

function renderBars(id, rows, maxRows=12) {
  const data=(rows || []).slice(0,maxRows); const max=Math.max(1,...data.map(r=>Number(r[1])));
  $(id).innerHTML=data.map(([label,value])=>`<div class="bar-row"><div class="bar-label" title="${escapeHtml(label)}">${escapeHtml(label)}</div><div class="bar-track"><div class="bar-fill" style="width:${(value/max)*100}%"></div></div><div class="bar-value">${number(value)}</div></div>`).join('');
}

function renderAnalytics() {
  const s=state.summary; if(!s) return;
  renderBars('categoryBars', s.categories, 14); renderBars('statusBars', s.statuses, 10);
  const years=(s.completion_years || []).filter(([year])=>Number(year)>=2024 && Number(year)<=2040); const max=Math.max(1,...years.map(r=>Number(r[1])));
  $('timelineBars').innerHTML=years.map(([year,count])=>`<div class="year-bar" title="${year}: ${count}" style="height:${Math.max(4,(count/max)*100)}%"><span>${year}</span></div>`).join('');
  $('topBudgetList').innerHTML=(s.top_budget_projects||[]).map((p,i)=>`<div class="rank-row"><div class="rank-no">${String(i+1).padStart(2,'0')}</div><div class="rank-name">${escapeHtml(p.project || 'Project')}<small>${escapeHtml(p.community || p.area || '')} / ${escapeHtml(p.category || '')}</small></div><div class="rank-budget">${money(p.budget)}</div></div>`).join('');
}

function radarRows() {
  const q=$('radarSearch').value.toLowerCase().trim(), mode=$('radarMatchFilter').value; const rows=state.radar?.matches || [];
  return rows.filter(item=>{ const first=item.matches?.[0]; const hay=[item.pipeline_project.project,item.pipeline_project.division,item.pipeline_project.description,first?.solicitation?.description,first?.solicitation?.document_number].join(' ').toLowerCase(); return (!q || hay.includes(q)) && (mode!=='matched' || (item.matches?.length||0)>0); });
}
function renderRadar() {
  if(!state.radar) return;
  $('radarMetrics').innerHTML=[['PIPELINE',state.radar.pipeline_total],['OPEN BIDS',state.radar.open_solicitation_total],['CANDIDATE LINKS',state.radar.projects_with_candidate_matches]].map(([l,v])=>`<div class="radar-metric"><span>${l}</span><strong>${number(v)}</strong></div>`).join('');
  const rows = radarRows();
  $('radarBody').innerHTML=rows.length ? rows.map(item=>{ const p=item.pipeline_project, m=item.matches?.[0]; return `<tr><td><div class="project-title">${escapeHtml(p.project)}</div><div class="subtle">${escapeHtml(p.description || p.location || '')}</div></td><td>${escapeHtml(p.division || 'Not specified')}</td><td>${escapeHtml(p.procurement_window || 'Not specified')}</td><td>${m ? `<div class="project-title">${escapeHtml(m.solicitation.document_number || m.solicitation.rfx_type || 'Candidate solicitation')}</div><div class="subtle">${escapeHtml(m.solicitation.description || '')}</div>` : '<span class="subtle">No candidate live match</span>'}</td><td>${m ? `<span class="score-pill">${Math.round(m.score*100)}%</span>` : ''}</td></tr>`; }).join('') : '<tr><td class="empty-table" colspan="5">No pipeline projects match these filters.</td></tr>';
}

function bindUi() {
  document.querySelectorAll('.tab').forEach(btn=>btn.addEventListener('click',()=>{ document.querySelectorAll('.tab').forEach(x=>{ const active=x===btn; x.classList.toggle('is-active',active); x.setAttribute('aria-selected',String(active)); }); document.querySelectorAll('.view').forEach(v=>v.classList.toggle('is-active',v.id===`view-${btn.dataset.view}`)); if(btn.dataset.view==='portfolio') setTimeout(()=>window.dispatchEvent(new Event('resize')),50); }));
  ['categoryFilter','statusFilter','regionFilter','budgetFilter'].forEach(id=>$(id).addEventListener('change',applyFilters));
  $('resetFilters').addEventListener('click',()=>{ ['categoryFilter','statusFilter','regionFilter','budgetFilter'].forEach(id=>$(id).selectedIndex=0); applyFilters(); });
  $('radarSearch').addEventListener('input',renderRadar); $('radarMatchFilter').addEventListener('change',renderRadar);
}

async function load() {
  bindUi(); initializeMap(detail);
  try {
    // Load sequentially: both endpoints use the same upstream dataset and cache.
    // Parallel cold requests can needlessly double-hit the public CKAN service.
    const projectsPayload = await fetchJson('/api/projects?limit=10000');
    const summaryPayload = await fetchJson('/api/projects/summary');
    state.projects=projectsPayload.projects || []; state.summary=summaryPayload;
    optionList($('categoryFilter'), unique(state.projects.map(p=>p.category))); optionList($('statusFilter'), unique(state.projects.map(p=>p.status))); optionList($('regionFilter'), unique(state.projects.map(p=>p.region)));
    renderKpis(); renderAnalytics(); applyFilters(); $('dataState').textContent=`Live public data / ${number(state.projects.length)} records`;
  } catch (error) {
    $('dataState').textContent='Ontario Builds unavailable'; $('kpiStrip').innerHTML=`<div class="error-box" role="alert">${escapeHtml(error.message)}</div>`;
  }
  try { state.radar=await fetchJson('/api/toronto/opportunity-radar'); renderRadar(); } catch(error) { $('radarBody').innerHTML=`<tr><td colspan="5"><div class="error-box">${escapeHtml(error.message)}</div></td></tr>`; }
}

load();
