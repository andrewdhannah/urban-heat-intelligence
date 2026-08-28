const DEFAULT_QUESTION = 'Where should Phoenix prioritize a cooling intervention this afternoon?';
const TIE_THRESHOLD = 0.1;
const state = { mode: 'replay', requestId: 0, controller: null, map: null, heatLayer: null, markers: new Map(), candidates: [], payload: null, replayEnv: null, focused: null, focusMode: false, evidenceAnimating: null, heatOpacity: 0.65, basemap: 'standard' };
const $ = (id) => document.getElementById(id);
const text = (el, value) => { if (el) el.textContent = value ?? '—'; };
const num = (value, digits = 1, suffix = '') => value === null || value === undefined || value === '' || Number.isNaN(Number(value)) ? '—' : `${Number(value).toFixed(digits)}${suffix}`;
const coordLabel = (c) => Array.isArray(c) && c.length >= 2 &&
  Number.isFinite(Number(c[0])) && Number.isFinite(Number(c[1]))
  ? `${Number(c[1]).toFixed(4)}°N, ${Math.abs(Number(c[0])).toFixed(4)}°W`
  : 'Location unavailable';
const reducedMotion = () => window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const scrollBehavior = () => reducedMotion() ? 'auto' : 'smooth';
const titleCase = (s) => String(s || '').replaceAll('_', ' ').replace(/\b\w/g, (m) => m.toUpperCase());

function initMap() {
  if (!window.L || state.map) return;
  state.map = L.map('map', { zoomControl: true, attributionControl: true, preferCanvas: true }).setView([33.4484, -112.074], 12);
  // OpenStreetMap is a no-key fallback; it keeps the demonstration free of API-key watermarks.
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19, attribution: '&copy; OpenStreetMap contributors' }).addTo(state.map);
}
function clearMap() {
  if (!state.map) return;
  if (state.evidenceAnimating) { clearTimeout(state.evidenceAnimating); state.evidenceAnimating = null; }
  window.__lunaState_evidenceAnimating = state.evidenceAnimating;
  if (state.heatLayer) { state.map.removeLayer(state.heatLayer); state.heatLayer = null; }
  state.markers.forEach((m) => state.map.removeLayer(m));
  state.markers.clear();
  const d = $('cell-detail');
  if (d) d.hidden = true;
  window.__lunaHeatmapFeatureCount = 0;
}
function featureTemp(feature) { const p = feature?.properties || {}; return Number(p.average_temperature ?? p.temperature_celsius ?? p.temperature ?? p.temp_celsius ?? p.value); }
function colorFor(value, min, max) { const t = max === min ? .5 : Math.max(0, Math.min(1, (value - min) / (max - min))); const stops = ['#f2dfbf', '#e7b06c', '#cf704d', '#9c4539', '#6f302d']; return stops[Math.min(stops.length - 1, Math.floor(t * stops.length))]; }
function renderMap(payload) {
  initMap(); clearMap(); state.map.getContainer().classList.toggle('basemap-monochrome', state.basemap === 'monochrome'); const features = Array.isArray(payload?.heatmap?.features) ? payload.heatmap.features : []; window.__lunaHeatmapFeatureCount = features.length;
  const values = features.map(featureTemp).filter(Number.isFinite); const min = values.length ? Math.min(...values) : null; const max = values.length ? Math.max(...values) : null;
  text($('legend-min'), num(min, 1)); text($('legend-max'), num(max, 1)); if (!features.length) { text($('map-loading'), 'No usable measured field for this mode.'); return; }
  const cellWeight = 0.5;
  const cellColor = 'rgba(255,255,255,.50)';
  const cellFillOpacity = state.heatOpacity;
  state.heatLayer = L.geoJSON({ type: 'FeatureCollection', features }, {
    style: (f) => ({ color: cellColor, weight: cellWeight, fillColor: colorFor(featureTemp(f), min, max), fillOpacity: reducedMotion() ? cellFillOpacity : 0 }),
    onEachFeature: (f, layer) => layer.on('click', () => { const d = $('cell-detail'); d.hidden = false; d.replaceChildren(); const label = document.createElement('span'); label.textContent = 'Measured cell'; const strong = document.createElement('strong'); strong.textContent = num(featureTemp(f), 1, '°C'); d.append(label, strong); })
  }).addTo(state.map);
  (payload.ranked_candidates || []).forEach(addMarker);
  const bounds = state.heatLayer.getBounds();
  if (!bounds.isValid()) return;
  const mapId = state.requestId;
  if (reducedMotion()) {
    state.heatLayer.setStyle({ fillOpacity: cellFillOpacity });
    state.map.fitBounds(bounds.pad(.08));
    text($('map-loading'), '');
    return;
  }
    state.evidenceAnimating = setTimeout(() => {
      if (state.requestId !== mapId) return;
      state.heatLayer.setStyle({ fillOpacity: cellFillOpacity });
      state.evidenceAnimating = setTimeout(() => {
        if (state.requestId !== mapId) return;
        state.evidenceAnimating = null;
        window.__lunaState_evidenceAnimating = null;
        state.map.flyToBounds(bounds.pad(.10), { animate: true, duration: 0.9, maxZoom: 15 });
      }, 320);
    }, 180);
}
function addMarker(candidate) { if (!state.map || !Array.isArray(candidate.coordinate)) return; const [lon, lat] = candidate.coordinate; if (!Number.isFinite(lat) || !Number.isFinite(lon)) return; const node = document.createElement('span'); node.textContent = candidate.rank; node.setAttribute('aria-hidden', 'true'); const marker = L.marker([lat, lon], { icon: L.divIcon({ className: `candidate-marker marker-${candidate.rank}`, html: node.outerHTML, iconSize: [42, 42], iconAnchor: [21, 21] }), title: `Candidate ${candidate.rank}`, riseOnHover: true }).addTo(state.map); marker.on('click', () => focusCandidate(candidate.rank, true)); state.markers.set(candidate.rank, marker); }
function focusCandidate(rank, pan = false) { state.focused = Number(rank) > 0 ? Number(rank) : null; document.querySelectorAll('.candidate-card').forEach((card) => card.classList.toggle('focused', Number(card.dataset.rank) === state.focused)); state.markers.forEach((m, r) => m.getElement()?.classList.toggle('marker-focused', r === state.focused)); const marker = state.markers.get(state.focused); if (marker && pan && state.map) state.map.panTo(marker.getLatLng()); }
function parkLabel(parks) { if (!parks || parks.available === false) return 'Parks context unavailable'; if (parks.inside_park && typeof parks.inside_park === 'object') return `Inside mapped park${parks.inside_park.park_name ? `: ${parks.inside_park.park_name}` : ''}`; return 'No mapped park at candidate'; }
function removeReplayContext() { $('replay-env-context')?.remove(); }
function renderCandidates(payload) { const list = $('candidate-list'); list.replaceChildren(); const candidates = Array.isArray(payload?.ranked_candidates) ? payload.ranked_candidates : []; state.candidates = candidates; const status = payload?.conditions?.ranking_status; const explainer = $('candidate-explainer'); if (explainer) explainer.textContent = status === 'near_tie' ? 'Deterministic rank from the measured field. The hottest measured locations are nearly tied; context below is descriptive, not a score.' : 'Deterministic rank from the measured field. Context below is descriptive, not a score.'; if (!candidates.length) { const empty = document.createElement('p'); empty.className = 'empty-state'; empty.textContent = 'No candidate locations were returned for this mode.'; list.append(empty); return; }
  candidates.forEach((c) => { const card = document.createElement('article'); card.className = `candidate-card ${status === 'near_tie' ? 'near-tie' : ''}`; card.dataset.rank = c.rank; card.tabIndex = 0; card.setAttribute('aria-label', `Candidate ${c.rank}, ${num(c.observed_temp)} degrees Celsius`); card.addEventListener('mouseenter', () => focusCandidate(c.rank)); card.addEventListener('mouseleave', () => focusCandidate(-1)); card.addEventListener('focus', () => focusCandidate(c.rank)); card.addEventListener('click', () => focusCandidate(c.rank, true)); card.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); focusCandidate(c.rank, true); } });
    const eyebrow = document.createElement('span'); eyebrow.className = 'eyebrow'; eyebrow.textContent = status === 'near_tie' ? 'TOP THERMAL CLUSTER' : 'THERMAL CANDIDATE'; const h = document.createElement('h3'); h.textContent = `Candidate ${c.rank}`; const rank = document.createElement('span'); rank.className = 'rank'; rank.textContent = String(c.rank).padStart(2, '0'); const temp = document.createElement('div'); temp.className = 'temp'; temp.textContent = num(c.observed_temp, 2, '°C'); const delta = document.createElement('div'); delta.className = 'delta'; delta.textContent = `${num(c.delta_from_area_mean, 2, '°C')} vs area mean`; const divider = document.createElement('hr'); divider.className = 'candidate-divider'; const details = document.createElement('div'); details.className = 'candidate-details'; [['Coordinates', coordLabel(c.coordinate)]].forEach(([label, value]) => { const box = document.createElement('div'); const s = document.createElement('span'); s.textContent = label; const strong = document.createElement('strong'); strong.textContent = value; box.append(s, strong); details.append(box); }); const note = document.createElement('p'); note.className = 'candidate-note'; note.textContent = state.mode === 'replay' ? (status === 'near_tie' ? 'The hottest measured locations are nearly tied; local context does not change the thermal ranking.' : 'Measured temperature plus local context; local context does not affect the thermal ranking.') : 'Thermal candidate identified from the measured field; local context does not alter the thermal ranking.'; card.append(eyebrow, h, rank, temp, delta, divider, details, note); list.append(card); });
  if (state.mode === 'replay') renderRepresentativeContext();
  else removeReplayContext();
}
function renderRepresentativeContext() {
  removeReplayContext();
  const values = state.replayEnv;
  if (!values) return;
  const box = document.createElement('div'); box.id = 'replay-env-context'; box.className = 'ranking-callout';
  const strong = document.createElement('strong'); strong.textContent = 'Representative Replay environmental context';
  const detail = document.createElement('div'); detail.textContent = `Heat index ${num(values.heat_index, 1, '°C')} · Apparent temperature ${num(values.apparent_temp, 1, '°C')} · Humidity ${num(values.humidity, 0, '%')}`;
  const disclosure = document.createElement('small'); disclosure.textContent = 'Shared historical context for the captured afternoon — not a separate measurement for each candidate.';
  box.append(strong, detail, disclosure); $('ranking-callout')?.after(box);
}
function renderContext(payload) { const root = $('context-content'); root.replaceChildren(); const candidates = payload?.ranked_candidates || []; candidates.forEach((c) => { const ctx = c.candidate_context || {}; const canopy = ctx.canopy || {}; const parks = ctx.parks; const row = document.createElement('div'); row.className = 'context-row'; const left = document.createElement('span'); left.textContent = `Candidate ${c.rank}`; const right = document.createElement('strong'); const parts = []; if (canopy.available && canopy.tree_canopy_pct != null) parts.push(`Canopy ${num(canopy.tree_canopy_pct, 1, '%')}`); else if (canopy.available === false) parts.push('Canopy unavailable'); parts.push(parkLabel(parks)); right.textContent = parts.join(' · '); row.append(left, right); root.append(row); }); const disclosure = document.createElement('div'); disclosure.className = 'context-disclosure'; disclosure.textContent = 'Phoenix GIS describes what surrounds each candidate and does not affect the thermal ranking (used_in_decision = false). A missing GIS result is not interpreted as "no mapped park."'; root.append(disclosure); }
function renderBrief(payload) { const root = $('brief-content'); root.replaceChildren(); const brief = payload?.urban_heat_brief; if (!brief) { const p = document.createElement('p'); p.className = 'muted'; p.textContent = 'Brief unavailable because no usable thermal evidence was returned.'; root.append(p); return; } (brief.sections || []).forEach((section) => { const wrap = document.createElement('section'); wrap.className = 'brief-section'; const h = document.createElement('h3'); h.textContent = section.heading; wrap.append(h); (section.claims || []).forEach((claim) => { const item = document.createElement('div'); item.className = 'claim'; const dot = document.createElement('span'); dot.className = 'claim-marker'; const body = document.createElement('div'); body.append(document.createTextNode(claim.text)); const meta = document.createElement('span'); meta.className = 'claim-meta'; meta.textContent = `${claim.source_provider || 'Source unavailable'} · ${claim.used_in_decision ? 'used in decision' : 'context only'}`; body.append(meta); item.append(dot, body); wrap.append(item); }); root.append(wrap); }); }
function renderEvidence(payload) { const root = $('evidence-content'); root.replaceChildren(); (payload?.evidence_chain || []).forEach((node, index) => { const item = document.createElement('div'); item.className = 'chain-node'; const n = document.createElement('b'); n.textContent = String(index + 1).padStart(2, '0'); const body = document.createElement('div'); const h = document.createElement('h3'); h.textContent = titleCase(node.step); const p = document.createElement('p'); const data = node.data || {}; p.textContent = data.provider ? `${data.provider}${data.used_in_decision === false ? ' · context only' : ''}` : data.rationale || data.summary || data.reason || 'Recorded application evidence event.'; const small = document.createElement('small'); small.textContent = node.timestamp || 'timestamp unavailable'; body.append(h, p, small); item.append(n, body); root.append(item); }); }
function clearResultSurfaces(message = 'Waiting for usable evidence.') {
  state.payload = null;
  state.candidates = [];
  state.replayEnv = null;
  state.focused = null;
  removeReplayContext();
  clearMap();
  updateNwsSource(null);
  closeSourcePopovers();
  text($('legend-min'), '—');
  text($('legend-max'), '—');
  text($('stat-mean'), '—');
  text($('stat-range'), '—');
  text($('stat-cells'), '—');
  text($('answer-hero'), message);
  text($('answer-summary'), 'No prior-mode evidence is retained on this surface.');
  $('ranking-callout').hidden = true;
  $('ranking-callout').replaceChildren();
  renderCandidates({ ranked_candidates: [] });
  renderBrief({});
  renderContext({});
  renderEvidence({});
}
function setLoading(message, mode) {
  $('status-region').replaceChildren();
  clearResultSurfaces('Loading the decision…');
  text($('stat-obs-time'), 'Loading…');
  text($('observation-note'), message);
  text($('mode-badge'), mode.toUpperCase());
  $('mode-badge').className = `mode-badge ${mode}`;
  text($('map-source-label'), `FortyGuard · ${mode === 'replay' ? 'Replay' : 'Live'}`);
  text($('map-loading'), message);
}
function showError(payload, mode) { const region = $('status-region'); region.replaceChildren(); const p = document.createElement('p'); const reason = payload?.why_this_answer || payload?.answer?.why_this_answer || payload?.message || ''; p.textContent = mode === 'live' && /last \d+ hours|freshness window|bounded freshness|No usable FortyGuard observation/i.test(reason) ? 'LIVE UNAVAILABLE — No usable FortyGuard observation was available within the bounded freshness window.' : mode === 'live' ? 'LIVE UNAVAILABLE — The current Live request could not be completed.' : 'Unable to load Replay evidence.'; region.append(p); if (mode === 'live') { const button = document.createElement('button'); button.className = 'mode-button'; button.type = 'button'; button.textContent = 'Try Replay'; button.addEventListener('click', () => request('replay')); region.append(button); } }
function renderError(payload, mode) {
  clearResultSurfaces(mode === 'live' ? 'Live evidence unavailable.' : 'Replay evidence unavailable.');
  text($('stat-obs-time'), 'Unavailable');
  text($('observation-note'), mode === 'live'
    ? 'Live request did not return usable evidence.'
    : 'Replay request did not return usable evidence.');
  showError(payload, mode);
  renderEvidence(payload || {});
}
function render(payload, mode) {
  state.mode = mode;
  state.payload = payload;
  state.replayEnv = mode === 'replay' ? payload?.priority_location?.env_params || null : null;
  const error = payload?.error === true || payload?.answer?.error === true;
  if (error) { renderError(payload, mode); return; }
  const conditions = payload.conditions || {};
  updateNwsSource(payload);
  const ranked = payload.ranked_candidates || conditions.ranked_candidates || [];
  const observation = payload.observation_time || payload.answer?.observation_time || payload.heatmap?.observation_time;
  const isNearTie = conditions.ranking_status === 'near_tie';
  text($('answer-hero'), ranked.length ? (isNearTie ? `${ranked.length} locations form the top thermal cluster.` : `Start with candidate ${ranked[0].rank}.`) : 'Measured field loaded.');
  text($('answer-summary'), payload.summary || payload.answer?.summary || 'Thermal evidence is ready for investigation.');
  text($('stat-mean'), num(conditions.area_mean_temperature_celsius, 1, '°C'));
  text($('stat-range'), num(conditions.area_temperature_range_celsius, 1, '°C'));
  text($('stat-cells'), conditions.feature_count ?? payload.heatmap?.feature_count ?? '—');
  text($('stat-obs-time'), observation || 'Unavailable');
  text($('observation-note'), mode === 'replay' ? 'Historical provider capture · reproducible' : 'Latest available provider workflow · time surfaced');
  text($('mode-badge'), mode.toUpperCase());
  $('mode-badge').className = `mode-badge ${mode}`;
  text($('map-source-label'), `FortyGuard · ${mode === 'replay' ? 'Replay' : 'Live'}`);
  const callout = $('ranking-callout');
  callout.hidden = !ranked.length;
  callout.replaceChildren();
  if (isNearTie) { const strong = document.createElement('strong'); strong.textContent = 'Near tie · thermal evidence alone does not distinguish'; callout.append(strong, document.createTextNode(` Spread remains within ${num(conditions.tie_threshold_celsius ?? TIE_THRESHOLD, 1, '°C')}.`)); }
  else if (ranked.length) { const strong = document.createElement('strong'); strong.textContent = `Candidate ${ranked[0].rank} leads the measured field.`; callout.append(strong); }
  renderMap(payload);
  renderCandidates({ ranked_candidates: ranked, conditions });
  renderBrief(payload);
  renderContext(payload);
  renderEvidence(payload);
}

const INTENTS = [
  { id: 'mode', keys: ['show live data', 'use live', 'switch to live', 'show replay', 'use replay', 'switch to replay'],
    answer: (_q, target) => `Switching to ${target === 'live' ? 'Live' : 'Replay'} mode.`,
    source: 'Mode control · explicit user action required', why: 'Replay and Live have different freshness and network semantics.', suggestions: ['Show me the evidence', 'Compare the candidates'] },
  { id: 'priority', keys: ['where', 'hottest', 'top locations', 'priority'], answer: () => `The loaded ${state.mode.toUpperCase()} evidence identifies ${state.candidates.length || 'no'} candidate locations for investigation. FortyGuard measured thermal observations determine the ordering.`, source: 'FortyGuard · measured evidence', why: 'These thermal observations are the evidence used to identify and compare candidate locations.', suggestions: ['Why are these locations tied?', 'Compare tree canopy', 'Show me the evidence'] },
  { id: 'compare', keys: ['compare', 'different', 'candidates'], answer: () => { const rows = state.candidates.map((c) => `Candidate ${c.rank}: ${num(c.observed_temp, 2, '°C')}, ${num(c.delta_from_area_mean, 2, '°C')} vs area mean`).join(' · '); return rows || 'No candidates are loaded to compare.'; }, source: 'FortyGuard · measured evidence', why: 'These thermal observations show how each candidate compares with the surrounding measured field.', suggestions: ['Compare canopy', 'Which candidate is in a park?'] },
  { id: 'tie', keys: ['tie', 'winner', 'close'], answer: () => state.payload?.conditions?.ranking_status === 'near_tie' ? `There is no meaningful thermal winner: the top ${state.candidates.length} locations are within the ${num(state.payload.conditions.tie_threshold_celsius ?? TIE_THRESHOLD, 1, '°C')} threshold. Deterministic ranks remain, but all are comparable investigation priorities.` : 'The loaded ranking is not marked as a near tie.', source: 'FortyGuard · measured evidence', why: 'These thermal observations are the evidence used to identify and compare candidate locations.', suggestions: ['Compare the candidates', 'Show me the evidence'] },
  { id: 'canopy', keys: ['canopy', 'tree cover', 'trees'], answer: () => state.candidates.map((c) => {
      const canopy = c.candidate_context?.canopy;
      const value = canopy?.available === true ? canopy.tree_canopy_pct : null;
      return `Candidate ${c.rank}: ${value == null ? 'canopy context unavailable' : num(value, 1, '%')}`;
    }).join(' · ') || 'Canopy context is unavailable.', source: 'Phoenix GIS · context only · not used to rank', why: 'This describes local conditions around thermal candidates but does not change their ranking.', action: () => document.querySelector('.context-panel')?.scrollIntoView({ behavior: scrollBehavior() }), suggestions: ['Which candidates are in mapped parks?', 'Is canopy used to rank them?'] },
  { id: 'parks', keys: ['park', 'parks'], answer: () => state.candidates.map((c) => `Candidate ${c.rank}: ${parkLabel(c.candidate_context?.parks)}`).join(' · ') || 'Park context is unavailable.', source: 'Phoenix GIS · context only · not used to rank', why: 'This describes local conditions around thermal candidates but does not change their ranking.', action: () => document.querySelector('.context-panel')?.scrollIntoView({ behavior: scrollBehavior() }), suggestions: ['Compare canopy', 'Show the measured field'] },
  { id: 'weather', keys: ['nws', 'weather', 'happening now', 'forecast'],
    answer: () => {
      if (state.mode === 'replay') return 'Current NWS context is not included in historical Replay.';
      const status = state.payload?.nws_context?.evidence_status;
      return status === 'supplemental_context'
        ? 'NWS provides supplemental current/forecast context; it does not determine the thermal ranking.'
        : 'NWS supplemental context is unavailable in the loaded result.';
    },
    source: 'NWS · supplemental context', why: 'This provides broader atmospheric context and does not determine candidate ordering.', suggestions: ['Show me the evidence'] },
  { id: 'evidence', keys: ['trust', 'evidence', 'data came', 'provenance'], answer: () => 'The answer is grounded in the loaded evidence chain: FortyGuard measured the thermal field and determines ordering; Phoenix GIS and NWS are contextual and do not re-rank candidates.', source: 'Evidence chain · source roles preserved', why: 'It shows how the answer was assembled and which sources support each part of the decision.', action: () => openEvidence(), suggestions: ['Compare the candidates', 'Focus the map'] },
  { id: 'map', keys: ['show candidate', 'focus the map', 'measured cell', 'map'], answer: () => 'The measured FortyGuard field is now the primary surface. Candidate markers remain synchronized with the comparison cards.', source: 'FortyGuard · measured evidence', action: () => { const match = $('question-input').value.match(/candidate\s+(\d+)/i); if (match) focusCandidate(Number(match[1]), true); else setFocusMode(true); }, suggestions: ['Show me the evidence', 'Compare the candidates'] },
  { id: 'unsupported', keys: ['plant', 'planting', 'trees would', 'cool most', 'effect', 'reduce', 'benefit most', 'work best', 'efficacy'], answer: () => 'The current evidence can compare measured heat and available local context, but it does not estimate the cooling effect or efficacy of a specific intervention.', source: 'Governed analytical scope', why: 'The available evidence does not estimate intervention effectiveness.', suggestions: ['Compare the candidates', 'Show me the evidence'] }
];
function parseIntent(question) { const q = question.toLowerCase(); const unsupported = INTENTS.find((intent) => intent.id === 'unsupported' && intent.keys.some((key) => q.includes(key))); if (unsupported && /(plant|planting|trees would|cool most|cooling effect|reduce|benefit most|how many degrees|work best|efficacy|intervention)/.test(q)) return unsupported; return INTENTS.find((intent) => intent.id !== 'unsupported' && intent.keys.some((key) => q.includes(key))) || INTENTS[0]; }
function requestedMode(question) { return /\blive\b/i.test(question) ? 'live' : 'replay'; }
function runAnalyst(question) {
  const intent = parseIntent(question);
  const targetMode = intent.id === 'mode' ? requestedMode(question) : state.mode;
  const result = $('analyst-result'); result.replaceChildren();
  const label = document.createElement('span'); label.className = 'eyebrow accent'; label.textContent = 'GROUNDED ANALYST';
  const answer = document.createElement('p'); answer.textContent = intent.answer(question, targetMode);
  const source = document.createElement('small'); source.textContent = `Source: ${intent.source} · Why it matters: ${intent.why || 'This source directly supports the answer.'}`;
  result.append(label, answer, source);
  const suggestions = $('analyst-suggestions'); suggestions.replaceChildren();
  intent.suggestions.filter((s) => !(state.mode === 'replay' && /NWS|weather|current/i.test(s))).slice(0, 3).forEach((suggestion) => { const b = document.createElement('button'); b.type = 'button'; b.textContent = suggestion; b.addEventListener('click', () => { $('question-input').value = suggestion; runAnalyst(suggestion); }); suggestions.append(b); });
  intent.action?.();
  if (intent.id === 'mode') request(targetMode);
}
function openEvidence() { const drawer = $('evidence-drawer'); drawer.hidden = false; $('evidence-toggle').setAttribute('aria-expanded', 'true'); drawer.scrollIntoView({ behavior: scrollBehavior(), block: 'start' }); }
function setFocusMode(enabled) { state.focusMode = enabled; document.body.classList.toggle('map-focus', enabled); $('map-focus-button').textContent = enabled ? 'Exit map focus' : 'Focus map'; $('map-focus-button').setAttribute('aria-pressed', String(enabled)); $('focus-exit-layer').hidden = !enabled; $('focus-exit-button').setAttribute('aria-pressed', String(enabled)); if (enabled) $('focus-exit-button').focus(); setTimeout(() => state.map?.invalidateSize(), 20); }
async function request(mode = state.mode) {
  const id = ++state.requestId;
  state.mode = mode;
  if (state.controller) state.controller.abort();
  state.controller = new AbortController();
  setLoading(mode === 'replay' ? 'Loading reproducible capture…' : 'Requesting latest available provider observation…', mode);
  $('btn-replay').classList.toggle('active', mode === 'replay');
  $('btn-live').classList.toggle('active', mode === 'live');
  $('btn-replay').setAttribute('aria-pressed', String(mode === 'replay'));
  $('btn-live').setAttribute('aria-pressed', String(mode === 'live'));
  try {
    const q = encodeURIComponent($('question-input').value || DEFAULT_QUESTION);
    const response = await fetch(`/api/answer?question=${q}&mode=${mode}`, { signal: state.controller.signal });
    let payload = null;
    try { payload = await response.json(); }
    catch { payload = { error: true, message: 'Invalid server response', mode }; }
    if (id !== state.requestId) return;
    if (!response.ok) payload = { ...(payload || {}), error: true, mode };
    render(payload || { error: true, mode }, mode);
  } catch (error) {
    if (error.name !== 'AbortError' && id === state.requestId)
      renderError({ error: true, message: 'Request unavailable', mode }, mode);
  }
}
const SOURCE_COPY = { fortyguard: { source: 'FortyGuard', what: 'Real provider thermal observations across the loaded measured field.', why: 'This measured field identifies and orders candidate locations.', role: 'USED TO RANK', time: () => state.mode === 'live' ? 'FortyGuard Live workflow; latest usable observation returned by the governed request. Observation/effective time is surfaced above.' : 'Genuine FortyGuard provider response captured for reproducibility. Historical Replay — not current Live data.' }, gis: { source: 'City of Phoenix GIS', what: 'Tree-canopy and mapped-park context around candidate locations.', why: 'It helps explain how candidate environments differ after thermal candidates are identified.', role: 'CONTEXT ONLY · NOT USED TO RANK', time: 'Reference periods and availability come from the loaded payload.' }, nws: { source: 'National Weather Service', what: 'Current or forecast atmospheric context.', why: 'It helps interpret broader heat conditions without changing thermal ordering.', role: 'SUPPLEMENTAL · NOT USED TO RANK', time: () => state.mode === 'live'
      ? 'Shown only when usable Live NWS context is present in the loaded result.'
      : 'Current NWS context is excluded from historical Replay.' }, brief: { source: 'Urban Heat Brief', what: 'Derived interpretation composed from normalized application evidence.', why: 'It summarizes the loaded evidence in bounded language for decision support.', role: 'DERIVED INTERPRETATION', time: 'Claim lineage is available in Inspect Evidence.' } };
function showSourcePopover(key, control) { const pop = document.querySelector(`[data-popover="${key}"]`); const copy = SOURCE_COPY[key]; if (!pop || !copy) return; pop.replaceChildren(); [['SOURCE', copy.source], ['WHAT', copy.what], ['WHY IT MATTERS', copy.why], ['ROLE', copy.role], ['TIME / MODE', typeof copy.time === 'function' ? copy.time() : copy.time]].forEach(([label, value]) => { const row = document.createElement('div'); const name = document.createElement('b'); name.textContent = label; const detail = document.createElement('span'); detail.textContent = value; row.append(name, detail); pop.append(row); }); pop.hidden = false; control.setAttribute('aria-expanded', 'true'); }
function sourcePopover(control) {
  return document.querySelector(`[data-popover="${control.dataset.source}"]`);
}
function closeSourcePopovers() {
  document.querySelectorAll('.source-popover').forEach((pop) => {
    pop.hidden = true;
    delete pop.dataset.pinned;
    delete pop.dataset.hovered;
  });
  document.querySelectorAll('.source-control')
    .forEach((button) => button.setAttribute('aria-expanded', 'false'));
}
function maybeClosePopover(control) {
  const pop = sourcePopover(control);
  if (!pop || pop.dataset.pinned || pop.dataset.hovered || control.matches(':focus')) return;
  pop.hidden = true;
  control.setAttribute('aria-expanded', 'false');
}
function initSourceControls() {
  document.querySelectorAll('.source-control').forEach((control) => {
    const pop = sourcePopover(control);
    if (!pop) return;
    control.addEventListener('mouseenter', () => showSourcePopover(control.dataset.source, control));
    control.addEventListener('mouseleave', () => setTimeout(() => maybeClosePopover(control), 0));
    pop.addEventListener('mouseenter', () => { pop.dataset.hovered = 'true'; });
    pop.addEventListener('mouseleave', () => {
      delete pop.dataset.hovered;
      setTimeout(() => maybeClosePopover(control), 0);
    });
    control.addEventListener('click', (event) => {
      event.stopPropagation();
      if (pop.dataset.pinned) { closeSourcePopovers(); return; }
      closeSourcePopovers();
      showSourcePopover(control.dataset.source, control);
      pop.dataset.pinned = 'true';
    });
    control.addEventListener('focus', () => showSourcePopover(control.dataset.source, control));
    control.addEventListener('blur', () => setTimeout(() => maybeClosePopover(control), 0));
    pop.addEventListener('click', (event) => event.stopPropagation());
  });
  document.addEventListener('click', closeSourcePopovers);
}
function updateNwsSource(payload) {
  const active = payload?.mode === 'live' &&
    payload?.nws_context?.evidence_status === 'supplemental_context';
  $('nws-source-line').hidden = !active;
}
function handleEscape(event) {
  if (event.key !== 'Escape') return;
  const open = [...document.querySelectorAll('.source-popover')].find((pop) => !pop.hidden);
  if (open) {
    event.preventDefault();
    event.stopImmediatePropagation();
    closeSourcePopovers();
    return;
  }
  if (state.focusMode) {
    event.preventDefault();
    setFocusMode(false);
    $('map-focus-button').focus();
  }
}
function initHeatOpacityControl() {
  const input = $('heat-opacity');
  const output = $('heat-opacity-value');
  if (!input || !output) return;
  input.value = String(Math.round(state.heatOpacity * 100));
  output.textContent = `${input.value}%`;
  const apply = () => {
    state.heatOpacity = Number(input.value) / 100;
    output.textContent = `${input.value}%`;
    if (state.heatLayer) state.heatLayer.setStyle({ fillOpacity: state.heatOpacity });
    window.__lunaHeatOpacity = state.heatOpacity;
  };
  input.addEventListener('input', apply);
  window.__lunaHeatOpacity = state.heatOpacity;
}
function initBasemapControl() {
  const standard = $('basemap-standard');
  const mono = $('basemap-monochrome-btn');
  if (!standard || !mono) return;
  const apply = (mode) => {
    state.basemap = mode;
    const container = state.map?.getContainer();
    if (container) container.classList.toggle('basemap-monochrome', mode === 'monochrome');
    standard.classList.toggle('active', mode === 'standard');
    mono.classList.toggle('active', mode === 'monochrome');
    standard.setAttribute('aria-pressed', String(mode === 'standard'));
    mono.setAttribute('aria-pressed', String(mode === 'monochrome'));
  };
  standard.addEventListener('click', () => apply('standard'));
  mono.addEventListener('click', () => apply('monochrome'));
  apply('standard');
}
function init() { $('question-input').value = DEFAULT_QUESTION; initSourceControls(); initMap(); initHeatOpacityControl(); initBasemapControl(); $('question-form').addEventListener('submit', (e) => { e.preventDefault(); const q = $('question-input').value.trim(); if (q && q !== DEFAULT_QUESTION) runAnalyst(q); else request(state.mode); }); $('btn-replay').addEventListener('click', () => request('replay')); $('btn-live').addEventListener('click', () => request('live')); $('map-focus-button').addEventListener('click', () => setFocusMode(!state.focusMode)); $('focus-exit-button').addEventListener('click', () => setFocusMode(false)); document.addEventListener('keydown', handleEscape); $('evidence-close').addEventListener('click', () => { $('evidence-drawer').hidden = true; $('evidence-toggle').setAttribute('aria-expanded', 'false'); }); $('evidence-toggle').addEventListener('click', openEvidence); request('replay'); }
window.addEventListener('DOMContentLoaded', init);
