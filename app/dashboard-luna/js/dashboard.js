const DEFAULT_QUESTION = 'Where should Phoenix prioritize a cooling intervention this afternoon?';
const TIE_THRESHOLD = 0.1;
const state = { mode: 'replay', requestId: 0, controller: null, map: null, heatLayer: null, aoiLayer: null, measuredAreaBounds: null, markers: new Map(), candidates: [], payload: null, replayEnv: null, focused: null, focusMode: false, evidenceAnimating: null, heatOpacity: 0.65, basemap: 'standard', liveStart: 0, liveTimer: null, unit: 'C' };
const $ = (id) => document.getElementById(id);
const text = (el, value) => { if (el) el.textContent = value ?? '—'; };
const num = (value, digits = 1, suffix = '') => value === null || value === undefined || value === '' || Number.isNaN(Number(value)) ? '—' : `${Number(value).toFixed(digits)}${suffix}`;
// P1-R1: Global °C/°F conversion helpers — presentation-only; evidence remains canonical.
function toF(c) { return c * 9 / 5 + 32; }
function deltaF(dc) { return dc * 9 / 5; } // deltas/ranges: no +32
function unitSymbol() { return state.unit === 'F' ? '°F' : '°C'; }
function tempD(c) { return c == null ? '—' : (state.unit === 'F' ? num(toF(c), 1, '°F') : num(c, 1, '°C')); }
function tempD2(c) { return c == null ? '—' : (state.unit === 'F' ? num(toF(c), 2, '°F') : num(c, 2, '°C')); }
function deltaD(dc) { return dc == null ? '—' : (state.unit === 'F' ? num(deltaF(dc), 2, '°F') : num(dc, 2, '°C')); }
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
  if (state.aoiLayer) { state.map.removeLayer(state.aoiLayer); state.aoiLayer = null; }
  state.measuredAreaBounds = null;
  const areaLabel = $('measured-area-label');
  if (areaLabel) areaLabel.hidden = true;
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
  text($('legend-min'), num(state.unit === 'F' ? toF(min) : min, 1)); text($('legend-max'), num(state.unit === 'F' ? toF(max) : max, 1)); text($('legend-unit'), unitSymbol()); if (!features.length) { text($('map-loading'), 'No usable measured field for this mode.'); return; }
  const cellWeight = 0.5;
  const cellColor = 'rgba(255,255,255,.50)';
  const cellFillOpacity = state.heatOpacity;
  state.heatLayer = L.geoJSON({ type: 'FeatureCollection', features }, {
    style: (f) => ({ color: cellColor, weight: cellWeight, fillColor: colorFor(featureTemp(f), min, max), fillOpacity: reducedMotion() ? cellFillOpacity : 0 }),
    onEachFeature: (f, layer) => layer.on('click', () => { const d = $('cell-detail'); d.hidden = false; d.replaceChildren(); const label = document.createElement('span'); label.textContent = 'Measured cell'; const strong = document.createElement('strong'); strong.textContent = tempD2(featureTemp(f)); d.append(label, strong); })
  }).addTo(state.map);
  (payload.ranked_candidates || []).forEach(addMarker);
  const bounds = state.heatLayer.getBounds();
  if (!bounds.isValid()) return;
  renderMeasuredArea(bounds, features.length);
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
function renderMeasuredArea(bounds, featureCount) {
  if (!state.map || !bounds || !bounds.isValid()) return;
  state.measuredAreaBounds = bounds;
  if (state.aoiLayer) { state.map.removeLayer(state.aoiLayer); state.aoiLayer = null; }
  // Subtle measured-area boundary derived from the actual returned evidence geometry.
  // Presentation only — never modifies evidence geometry or ranking.
  state.aoiLayer = L.rectangle(bounds, {
    color: '#145c70', weight: 2, dashArray: '6 4', fill: false, interactive: false, opacity: 0.7
  }).addTo(state.map);
  const label = $('measured-area-label');
  if (label) { label.textContent = `Measured area · ${featureCount} FortyGuard cells`; label.hidden = false; }
}
function fitMeasuredArea() {
  if (!state.map || !state.measuredAreaBounds || !state.measuredAreaBounds.isValid()) return;
  state.map.flyToBounds(state.measuredAreaBounds.pad(.10), { animate: !reducedMotion(), duration: 0.7, maxZoom: 15 });
}
function addMarker(candidate) { if (!state.map || !Array.isArray(candidate.coordinate)) return; const [lon, lat] = candidate.coordinate; if (!Number.isFinite(lat) || !Number.isFinite(lon)) return; const node = document.createElement('span'); node.textContent = candidate.rank; node.setAttribute('aria-hidden', 'true'); const marker = L.marker([lat, lon], { icon: L.divIcon({ className: `candidate-marker marker-${candidate.rank}`, html: node.outerHTML, iconSize: [42, 42], iconAnchor: [21, 21] }), title: `Candidate ${candidate.rank}`, riseOnHover: true, zIndexOffset: baseMarkerOffset(candidate.rank) }).addTo(state.map); marker.on('click', () => focusCandidate(candidate.rank, true)); state.markers.set(candidate.rank, marker); }
// Deterministic base stacking: Candidate 1 remains default foreground (highest base offset).
// Higher z-index offset renders on top. Focused candidate is elevated well above all others.
const FOCUS_Z_OFFSET = 1000;
function baseMarkerOffset(rank) { return 10 - Number(rank); }
function applyMarkerElevation() {
  state.markers.forEach((m, r) => {
    const focused = r === state.focused;
    m.setZIndexOffset(focused ? FOCUS_Z_OFFSET : baseMarkerOffset(r));
    m.getElement()?.classList.toggle('marker-focused', focused);
  });
}
function focusCandidate(rank, pan = false) { state.focused = Number(rank) > 0 ? Number(rank) : null; document.querySelectorAll('.candidate-card').forEach((card) => card.classList.toggle('focused', Number(card.dataset.rank) === state.focused)); applyMarkerElevation(); const marker = state.markers.get(state.focused); if (marker && pan && state.map) state.map.panTo(marker.getLatLng()); }
function parkLabel(parks) { if (!parks || parks.available === false) return 'Parks context unavailable'; if (parks.inside_park && typeof parks.inside_park === 'object') return `Inside mapped park${parks.inside_park.park_name ? `: ${parks.inside_park.park_name}` : ''}`; return 'No mapped park at candidate'; }
function removeReplayContext() { $('replay-env-context')?.remove(); }
function renderCandidates(payload) { const list = $('candidate-list'); list.replaceChildren(); const candidates = Array.isArray(payload?.ranked_candidates) ? payload.ranked_candidates : []; state.candidates = candidates; const status = payload?.conditions?.ranking_status; const explainer = $('candidate-explainer'); if (explainer) explainer.textContent = status === 'near_tie' ? 'Deterministic rank from the measured field. The hottest measured locations are nearly tied; context below is descriptive, not a score.' : 'Deterministic rank from the measured field. Context below is descriptive, not a score.'; if (!candidates.length) { const empty = document.createElement('p'); empty.className = 'empty-state'; empty.textContent = 'No candidate locations were returned for this mode.'; list.append(empty); return; }
  candidates.forEach((c) => { const card = document.createElement('article'); card.className = `candidate-card ${status === 'near_tie' ? 'near-tie' : ''}`; card.dataset.rank = c.rank; card.tabIndex = 0; card.setAttribute('aria-label', `Candidate ${c.rank}, ${tempD2(c.observed_temp)}`); card.addEventListener('mouseenter', () => focusCandidate(c.rank)); card.addEventListener('mouseleave', () => focusCandidate(-1)); card.addEventListener('focus', () => focusCandidate(c.rank)); card.addEventListener('click', () => focusCandidate(c.rank, true)); card.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); focusCandidate(c.rank, true); } });
    const eyebrow = document.createElement('span'); eyebrow.className = 'eyebrow'; eyebrow.textContent = status === 'near_tie' ? 'TOP THERMAL CLUSTER' : 'THERMAL CANDIDATE'; const h = document.createElement('h3'); h.textContent = `Candidate ${c.rank}`; const rank = document.createElement('span'); rank.className = 'rank'; rank.textContent = String(c.rank).padStart(2, '0'); const temp = document.createElement('div'); temp.className = 'temp'; temp.textContent = tempD2(c.observed_temp); const delta = document.createElement('div'); delta.className = 'delta'; delta.textContent = `${deltaD(c.delta_from_area_mean)} vs area mean`; const divider = document.createElement('hr'); divider.className = 'candidate-divider'; const details = document.createElement('div'); details.className = 'candidate-details'; [['Coordinates', coordLabel(c.coordinate)]].forEach(([label, value]) => { const box = document.createElement('div'); const s = document.createElement('span'); s.textContent = label; const strong = document.createElement('strong'); strong.textContent = value; box.append(s, strong); details.append(box); }); const note = document.createElement('p'); note.className = 'candidate-note'; note.textContent = state.mode === 'replay' ? (status === 'near_tie' ? 'The hottest measured locations are nearly tied; local context does not change the thermal ranking.' : 'Measured temperature plus local context; local context does not affect the thermal ranking.') : 'Thermal candidate identified from the measured field; local context does not alter the thermal ranking.'; card.append(eyebrow, h, rank, temp, delta, divider, details, note); list.append(card); });
  if (state.mode === 'replay') renderRepresentativeContext();
  else removeReplayContext();
}
function renderRepresentativeContext() {
  removeReplayContext();
  const values = state.replayEnv;
  if (!values) return;
  const box = document.createElement('div'); box.id = 'replay-env-context'; box.className = 'ranking-callout';
  const strong = document.createElement('strong'); strong.textContent = 'Representative Replay environmental context';
  const detail = document.createElement('div'); detail.textContent = `Heat index ${tempD(values.heat_index)} · Apparent temperature ${tempD(values.apparent_temp)} · Humidity ${num(values.humidity, 0, '%')}`;
  const disclosure = document.createElement('small'); disclosure.textContent = 'Shared historical context for the captured afternoon — not a separate measurement for each candidate.';
  box.append(strong, detail, disclosure); $('ranking-callout')?.after(box);
}
function renderContext(payload) { const root = $('context-content'); root.replaceChildren(); const candidates = payload?.ranked_candidates || []; candidates.forEach((c) => { const ctx = c.candidate_context || {}; const canopy = ctx.canopy || {}; const parks = ctx.parks; const row = document.createElement('div'); row.className = 'context-row'; const left = document.createElement('span'); left.textContent = `Candidate ${c.rank}`; const right = document.createElement('strong'); const parts = []; if (canopy.available && canopy.tree_canopy_pct != null) parts.push(`Canopy ${num(canopy.tree_canopy_pct, 1, '%')}`); else if (canopy.available === false) parts.push('Canopy unavailable'); parts.push(parkLabel(parks)); right.textContent = parts.join(' · '); row.append(left, right); root.append(row); }); const disclosure = document.createElement('div'); disclosure.className = 'context-disclosure'; disclosure.textContent = 'Phoenix GIS describes what surrounds each candidate and does not affect the thermal ranking (used_in_decision = false). A missing GIS result is not interpreted as "no mapped park."'; root.append(disclosure); }
function renderBrief(payload) { const root = $('brief-content'); root.replaceChildren(); const brief = payload?.urban_heat_brief; if (!brief) { const p = document.createElement('p'); p.className = 'muted'; p.textContent = 'Brief unavailable because no usable thermal evidence was returned.'; root.append(p); return; } (brief.sections || []).forEach((section) => { const wrap = document.createElement('section'); wrap.className = 'brief-section'; const h = document.createElement('h3'); h.textContent = section.heading; wrap.append(h); (section.claims || []).forEach((claim) => { const item = document.createElement('div'); item.className = 'claim'; const dot = document.createElement('span'); dot.className = 'claim-marker'; const body = document.createElement('div'); body.append(document.createTextNode(claim.text)); const meta = document.createElement('span'); meta.className = 'claim-meta'; meta.textContent = `${claim.source_provider || 'Source unavailable'} · ${claim.used_in_decision ? 'used in decision' : 'context only'}`; body.append(meta); item.append(dot, body); wrap.append(item); }); root.append(wrap); }); }
function renderEvidence(payload) { const root = $('evidence-content'); root.replaceChildren(); (payload?.evidence_chain || []).forEach((node, index) => { const item = document.createElement('div'); item.className = 'chain-node'; const n = document.createElement('b'); n.textContent = String(index + 1).padStart(2, '0'); const body = document.createElement('div'); const h = document.createElement('h3'); h.textContent = titleCase(node.step); const p = document.createElement('p'); const data = node.data || {}; p.textContent = data.provider ? `${data.provider}${data.used_in_decision === false ? ' · context only' : ''}` : data.rationale || data.summary || data.reason || 'Recorded application evidence event.'; const small = document.createElement('small'); small.textContent = node.timestamp || 'timestamp unavailable'; body.append(h, p, small); item.append(n, body); root.append(item); }); }
function clearResultSurfaces(message = 'Waiting for usable evidence.') {
  document.body.classList.remove('has-result');
  clearLiveTimer();
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
  text($('legend-unit'), unitSymbol());
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
// P1-R1: Compact NWS forecast banner — Live only, clearly labeled as forecast (not station observation)
function renderNwsForecast(payload) {
  const banner = $('nws-forecast-banner');
  if (!banner) return;
  banner.hidden = true;
  banner.replaceChildren();
  if (payload?.mode !== 'live') return;
  const nws = payload?.nws_context;
  if (!nws || nws.evidence_status !== 'supplemental_context') return;
  const cond = nws.conditions;
  if (!cond && (!nws.alerts || nws.alerts.length === 0)) return;
  banner.hidden = false;
  const label = document.createElement('span'); label.className = 'nws-label'; label.textContent = 'NWS FORECAST · SUPPLEMENTAL · NOT USED TO RANK';
  banner.append(label);
  if (cond) {
    const nwsTempC = cond.temperature_f != null ? (cond.temperature_f - 32) * 5 / 9 : null;
    const temp = document.createElement('div'); temp.className = 'nws-temp';
    temp.textContent = `${tempD(nwsTempC)} · ${cond.short_forecast || '—'}`;
    const detail = document.createElement('div'); detail.className = 'nws-detail';
    detail.textContent = `Wind: ${cond.wind_speed || '—'} ${cond.wind_direction || ''} · Period: ${cond.period_name || '—'}`;
    banner.append(temp, detail);
  }
  if (nws.alerts && nws.alerts.length > 0) {
    nws.alerts.forEach((a) => { const alert = document.createElement('div'); alert.className = 'nws-alert'; alert.textContent = `⚠ ${a.event || 'Alert'}: ${a.headline || ''}`; banner.append(alert); });
  }
  const disc = document.createElement('div'); disc.className = 'nws-disclosure'; disc.textContent = 'Forecast-period data from NWS — not a station observation. FortyGuard measured thermal field determines candidate ranking.';
  banner.append(disc);
}
// P1-R1: Historical NWS context for Replay — station observation + hazards, combined
function renderHistoricalNwsContext(payload) {
  const banner = $('nws-forecast-banner');
  if (!banner || payload?.mode !== 'replay') { banner.hidden = true; return; }
  const obs = payload?.historical_nws_obs;
  const ha = payload?.historical_alerts;
  const tempVal = obs?.temperature?.value;
  const hasObs = tempVal != null;
  const cp = ha?.consumer_projection;
  const hasAlerts = cp && cp.active_hazards && cp.active_hazards.length > 0;
  if (!hasObs && !hasAlerts) { banner.hidden = true; return; }

  banner.hidden = false;
  banner.replaceChildren();

  const label = document.createElement('span'); label.className = 'nws-label';
  label.textContent = 'HISTORICAL NWS · REPLAY · NOT USED TO RANK';
  banner.append(label);

  // Station observation (primary for "what was the weather" question)
  if (hasObs) {
    const temp = document.createElement('div'); temp.className = 'nws-temp';
    temp.textContent = `${tempD(tempVal)} · ${obs.text_description || '—'}`;
    const detail = document.createElement('div'); detail.className = 'nws-detail';
    detail.textContent = `Station: ${obs.station_identifier || 'KPHX'} · ${obs.observation_timestamp || '—'} (≈${obs.offset_minutes || 0} min from Replay time)`;
    banner.append(temp, detail);
    const windVal = obs.wind_speed?.value;
    const windDir = obs.wind_direction?.value;
    const humVal = obs.relative_humidity?.value;
    if (windVal != null || humVal != null) {
      const wind = document.createElement('div'); wind.className = 'nws-detail';
      wind.textContent = `Wind: ${windVal != null ? `${windVal} ${obs.wind_speed.unitCode?.replace('wmoUnit:', '') || ''}` : '—'} from ${windDir || '—'}° · Humidity: ${humVal != null ? num(humVal, 0, '%') : '—'}`;
      banner.append(wind);
    }
  }

  // Deduplicated hazard context
  if (hasAlerts) {
    const hazards = cp.active_hazards;
    const hazLabel = document.createElement('div'); hazLabel.className = 'nws-detail';
    hazLabel.style.marginTop = '6px';
    hazLabel.textContent = `Active conditions: ${hazards.map(h => h.event).join(' and ')} (${hazards.length} concurrent hazard${hazards.length > 1 ? 's' : ''}, from ${cp.raw_message_count || 0} NWS messages)`;
    banner.append(hazLabel);
  }

  const disc = document.createElement('div'); disc.className = 'nws-disclosure';
  disc.textContent = 'NWS station observation is a point measurement; FortyGuard thermal cells measure spatial burden. Alerts provide atmospheric context; neither changes thermal ranking.';
  banner.append(disc);
}
function render(payload, mode) {
  state.mode = mode;
  state.payload = payload;
  state.replayEnv = mode === 'replay' ? payload?.priority_location?.env_params || null : null;
  const error = payload?.error === true || payload?.answer?.error === true;
  if (error) { renderError(payload, mode); return; }
  document.body.classList.add('has-result');
  renderNwsForecast(payload);
  renderHistoricalNwsContext(payload);
  const conditions = payload.conditions || {};
  updateNwsSource(payload);
  const ranked = payload.ranked_candidates || conditions.ranked_candidates || [];
  const observation = payload.observation_time || payload.answer?.observation_time || payload.heatmap?.observation_time;
  const isNearTie = conditions.ranking_status === 'near_tie';
  text($('answer-hero'), ranked.length ? (isNearTie ? `${ranked.length} locations form the top thermal cluster.` : `Start with candidate ${ranked[0].rank}.`) : 'Measured field loaded.');
  text($('answer-summary'), payload.summary || payload.answer?.summary || 'Thermal evidence is ready for investigation.');
  text($('stat-mean'), tempD(conditions.area_mean_temperature_celsius));
  text($('stat-range'), deltaD(conditions.area_temperature_range_celsius));
  text($('stat-cells'), conditions.feature_count ?? payload.heatmap?.feature_count ?? '—');
  text($('stat-obs-time'), observation || 'Unavailable');
  text($('observation-note'), mode === 'replay' ? 'Historical provider capture · reproducible' : 'Latest available provider workflow · time surfaced');
  text($('mode-badge'), mode.toUpperCase());
  $('mode-badge').className = `mode-badge ${mode}`;
  text($('map-source-label'), `FortyGuard · ${mode === 'replay' ? 'Replay' : 'Live'}`);
  const callout = $('ranking-callout');
  callout.hidden = !ranked.length;
  callout.replaceChildren();
  if (isNearTie) { const strong = document.createElement('strong'); strong.textContent = 'Near tie · thermal evidence alone does not distinguish'; callout.append(strong, document.createTextNode(` Spread remains within ${deltaD(conditions.tie_threshold_celsius ?? TIE_THRESHOLD)}.`)); }
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
  { id: 'priority', keys: ['where', 'hottest', 'top locations', 'priority'], answer: () => `The loaded ${state.mode.toUpperCase()} evidence identifies ${state.candidates.length || 'no'} candidate locations for investigation. FortyGuard measured thermal observations determine the ordering — it localizes where measured burden concentrates within the analyzed area. Contextual sources explain the broader conditions but do not change the ranking.`, source: 'FortyGuard · measured evidence', why: 'These thermal observations are the evidence used to identify and compare candidate locations.', suggestions: ['Why are these locations tied?', 'Compare tree canopy', 'Show me the evidence'] },
  { id: 'compare', keys: ['compare', 'different', 'candidates'], answer: () => { const rows = state.candidates.map((c) => `Candidate ${c.rank}: ${tempD2(c.observed_temp)}, ${deltaD(c.delta_from_area_mean)} vs area mean`).join(' · '); return rows ? `FortyGuard measured field comparison: ${rows}. Thermal evidence alone determines these values; local context does not alter them.` : 'No candidates are loaded to compare.'; }, source: 'FortyGuard · measured evidence', why: 'These thermal observations show how each candidate compares with the surrounding measured field.', suggestions: ['Compare canopy', 'Which candidate is in a park?'] },
  { id: 'tie', keys: ['tie', 'winner', 'close'], answer: () => state.payload?.conditions?.ranking_status === 'near_tie' ? `There is no meaningful thermal winner: the top ${state.candidates.length} locations are within the ${deltaD(state.payload.conditions.tie_threshold_celsius ?? TIE_THRESHOLD)} threshold. Deterministic ranks remain, but all are comparable investigation priorities.` : 'The loaded ranking is not marked as a near tie.', source: 'FortyGuard · measured evidence', why: 'These thermal observations are the evidence used to identify and compare candidate locations.', suggestions: ['Compare the candidates', 'Show me the evidence'] },
  { id: 'canopy', keys: ['canopy', 'tree cover', 'trees'], answer: () => { const canopyInfo = state.candidates.map((c) => {
      const canopy = c.candidate_context?.canopy;
      const value = canopy?.available === true ? canopy.tree_canopy_pct : null;
      return `Candidate ${c.rank}: ${value == null ? 'canopy context unavailable' : num(value, 1, '%')}`;
    }).join(' · ') || 'Canopy context is unavailable.'; return `Phoenix GIS canopy: ${canopyInfo}. FortyGuard identified these candidates by measured thermal burden; canopy describes the physical surroundings and does not change the ranking.`; }, source: 'Phoenix GIS · context only · not used to rank', why: 'This describes local conditions around thermal candidates but does not change their ranking.', action: () => document.querySelector('.context-panel')?.scrollIntoView({ behavior: scrollBehavior() }), suggestions: ['Which candidates are in mapped parks?', 'Is canopy used to rank them?'] },
  { id: 'parks', keys: ['park', 'parks'], answer: () => { const parkInfo = state.candidates.map((c) => `Candidate ${c.rank}: ${parkLabel(c.candidate_context?.parks)}`).join(' · ') || 'Park context is unavailable.'; return `Phoenix GIS parks: ${parkInfo}. FortyGuard determines thermal candidate ranking; park context explains the surroundings and does not alter the ranking.`; }, source: 'Phoenix GIS · context only · not used to rank', why: 'This describes local conditions around thermal candidates but does not change their ranking.', action: () => document.querySelector('.context-panel')?.scrollIntoView({ behavior: scrollBehavior() }), suggestions: ['Compare canopy', 'Show the measured field'] },
  { id: 'weather', keys: ['nws', 'weather', 'happening now', 'forecast'],
    answer: () => {
      if (state.mode === 'replay') {
        const obs = state.payload?.historical_nws_obs;
        const ha = state.payload?.historical_alerts;
        let parts = [];
        if (obs && obs.temperature?.value != null) {
          parts.push(`NWS station ${obs.station_identifier || 'KPHX'} observed ${tempD(obs.temperature.value)} and ${obs.text_description || 'conditions'} at ${obs.observation_timestamp || 'the Replay time'}.`);
        }
        const cp = ha?.consumer_projection;
        if (cp && cp.active_hazards && cp.active_hazards.length > 0) {
          const hazList = cp.active_hazards.map(h => h.event).join(' and ');
          parts.push(`Active conditions included ${hazList}.`);
        }
        if (parts.length === 0) {
          return 'No historical NWS context is available for the Replay time. FortyGuard measured the thermal field for the captured afternoon.';
        }
        parts.push('NWS describes broader point atmospheric conditions; FortyGuard supplies the spatial thermal field used to localize where measured burden concentrated. Neither changes thermal ranking.');
        return parts.join(' ');
      }
      const status = state.payload?.nws_context?.evidence_status;
      return status === 'supplemental_context'
        ? 'NWS provides supplemental forecast context — it describes broader atmospheric conditions and does not determine the thermal ranking. FortyGuard localizes where measured thermal burden concentrates within the analyzed area.'
        : 'NWS supplemental context is unavailable in the loaded result. FortyGuard thermal evidence remains the primary decision source.';
    },
    source: 'NWS · supplemental context', why: 'This provides broader atmospheric context and does not determine candidate ordering.', suggestions: ['Show me the evidence'] },
  { id: 'evidence', keys: ['trust', 'evidence', 'data came', 'provenance'], answer: () => 'The answer is grounded in the loaded evidence chain: FortyGuard measured the thermal field and determines ordering; Phoenix GIS and NWS are contextual and do not re-rank candidates.', source: 'Evidence chain · source roles preserved', why: 'It shows how the answer was assembled and which sources support each part of the decision.', action: () => openEvidence(), suggestions: ['Compare the candidates', 'Focus the map'] },
  { id: 'map', keys: ['show candidate', 'focus the map', 'measured cell', 'map'], answer: () => 'The measured FortyGuard field is now the primary surface. Candidate markers remain synchronized with the comparison cards.', source: 'FortyGuard · measured evidence', action: () => { const match = $('question-input').value.match(/candidate\s+(\d+)/i); if (match) focusCandidate(Number(match[1]), true); else setFocusMode(true); }, suggestions: ['Show me the evidence', 'Compare the candidates'] },
  { id: 'unsupported', keys: ['plant', 'planting', 'trees would', 'cool most', 'effect', 'reduce', 'benefit most', 'work best', 'efficacy'], answer: () => 'The current evidence can compare measured heat and available local context, but it does not estimate the cooling effect or efficacy of a specific intervention.', source: 'Governed analytical scope', why: 'The available evidence does not estimate intervention effectiveness.', suggestions: ['Compare the candidates', 'Show me the evidence'] },
  { id: 'not_understood', keys: [], answer: (_q) => `I don't have a governed answer for that question. Try one of the supported questions below.`, source: 'Governed analytical scope', why: 'The input did not match any recognized intent.', suggestions: ['Where should Phoenix prioritize cooling?', 'Compare the candidates', 'Why are these locations nearly tied?', 'Compare tree canopy', 'Where did this evidence come from?', 'What can this analysis not tell me?'] }
];
function parseIntent(question) { const q = question.toLowerCase(); const unsupported = INTENTS.find((intent) => intent.id === 'unsupported' && intent.keys.some((key) => q.includes(key))); if (unsupported && /(plant|planting|trees would|cool most|cooling effect|reduce|benefit most|how many degrees|work best|efficacy|intervention)/.test(q)) return unsupported; return INTENTS.find((intent) => intent.id !== 'unsupported' && intent.id !== 'not_understood' && intent.keys.some((key) => q.includes(key))) || INTENTS.find((intent) => intent.id === 'not_understood'); }
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
  // For not_understood: show the answer but do NOT trigger a request or mode switch
}
function openEvidence() { const drawer = $('evidence-drawer'); drawer.hidden = false; $('evidence-toggle').setAttribute('aria-expanded', 'true'); drawer.scrollIntoView({ behavior: scrollBehavior(), block: 'start' }); }
function setFocusMode(enabled) { state.focusMode = enabled; document.body.classList.toggle('map-focus', enabled); $('map-focus-button').textContent = enabled ? 'Exit map focus' : 'Focus map'; $('map-focus-button').setAttribute('aria-pressed', String(enabled)); $('focus-exit-layer').hidden = !enabled; $('focus-exit-button').setAttribute('aria-pressed', String(enabled)); if (enabled) $('focus-exit-button').focus(); setTimeout(() => state.map?.invalidateSize(), 20); }
function toggleUnit() { state.unit = state.unit === 'C' ? 'F' : 'C'; $('btn-unit').textContent = state.unit === 'F' ? '°F ' : '°C '; const small = document.createElement('small'); small.textContent = state.unit === 'F' ? '/ °C' : '/ °F'; $('btn-unit').append(small); $('btn-unit').classList.toggle('active', state.unit === 'F'); $('btn-unit').setAttribute('aria-pressed', String(state.unit === 'F')); if (state.payload) render(state.payload, state.mode); }
async function request(mode = state.mode) {
  const id = ++state.requestId;
  state.mode = mode;
  if (state.controller) state.controller.abort();
  state.controller = new AbortController();
  clearLiveTimer();
  setLoading(mode === 'replay' ? 'Loading reproducible capture…' : 'Requesting latest available provider observation…', mode);
  $('btn-replay').classList.toggle('active', mode === 'replay');
  $('btn-live').classList.toggle('active', mode === 'live');
  $('btn-replay').setAttribute('aria-pressed', String(mode === 'replay'));
  $('btn-live').setAttribute('aria-pressed', String(mode === 'live'));
  if (mode === 'live') startLiveTimer();
  try {
    const q = encodeURIComponent($('question-input').value || DEFAULT_QUESTION);
    const response = await fetch(`/api/answer?question=${q}&mode=${mode}`, { signal: state.controller.signal });
    clearLiveTimer();
    let payload = null;
    try { payload = await response.json(); }
    catch { payload = { error: true, message: 'Invalid server response', mode }; }
    if (id !== state.requestId) return;
    if (!response.ok) payload = { ...(payload || {}), error: true, mode };
    render(payload || { error: true, mode }, mode);
  } catch (error) {
    clearLiveTimer();
    if (error.name !== 'AbortError' && id === state.requestId) {
      const region = $('status-region');
      region.replaceChildren();
      const p = document.createElement('p');
      p.textContent = mode === 'live'
        ? 'LIVE UNAVAILABLE — The request did not return a usable result. The provider may still be processing; you can try again or switch to Replay.'
        : 'Unable to load Replay evidence.';
      region.append(p);
      if (mode === 'live') {
        const button = document.createElement('button');
        button.className = 'mode-button';
        button.type = 'button';
        button.textContent = 'Try Replay';
        button.addEventListener('click', () => request('replay'));
        region.append(button);
      }
    }
  }
}
const SOURCE_COPY = { fortyguard: { source: 'FortyGuard', what: 'Real provider thermal observations across the loaded measured field.', why: 'This measured field identifies and orders candidate locations.', role: 'USED TO RANK', time: () => state.mode === 'live' ? 'FortyGuard Live workflow; latest usable observation returned by the governed request. Observation/effective time is surfaced above.' : 'Genuine FortyGuard provider response captured for reproducibility. Historical Replay — not current Live data.' }, gis: { source: 'City of Phoenix GIS', what: 'Tree-canopy and mapped-park context around candidate locations.', why: 'It helps explain how candidate environments differ after thermal candidates are identified.', role: 'CONTEXT ONLY · NOT USED TO RANK', time: 'Reference periods and availability come from the loaded payload.' }, nws: { source: 'National Weather Service', what: 'Current or forecast atmospheric context.', why: 'It helps interpret broader heat conditions without changing thermal ordering.', role: 'SUPPLEMENTAL · NOT USED TO RANK', time: () => state.mode === 'live'
      ? 'Shown only when usable Live NWS context is present in the loaded result.'
      : 'Current NWS forecast excluded; frozen contemporaneous historical station observation and alert context included. Supplemental — not used to rank.' }, brief: { source: 'Urban Heat Brief', what: 'Derived interpretation composed from normalized application evidence.', why: 'It summarizes the loaded evidence in bounded language for decision support.', role: 'DERIVED INTERPRETATION', time: 'Claim lineage is available in Inspect Evidence.' } };
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
// P1-R1: Question catalogue — ONLY questions with implemented intents, mode-aware
const CATALOGUE_QUESTIONS = [
  { q: 'Where should Phoenix prioritize cooling?', intents: ['priority'] },
  { q: 'Compare the three candidates.', intents: ['compare'] },
  { q: 'Why are these locations nearly tied?', intents: ['tie'] },
  { q: 'What was the weather that afternoon?', intents: ['weather'] },
  { q: 'Compare tree canopy.', intents: ['canopy'] },
  { q: 'Which candidates are near parks?', intents: ['parks'] },
  { q: 'Where did this evidence come from?', intents: ['evidence'] },
  { q: 'What can this analysis not tell me?', intents: ['unsupported'] },
  { q: 'Focus Candidate N.', intents: ['map'] }
];
function initQuestionCatalogue() {
  const list = $('catalogue-list');
  if (!list) return;
  list.replaceChildren();
  CATALOGUE_QUESTIONS.forEach((item) => {
    const b = document.createElement('button');
    b.type = 'button';
    b.textContent = item.q;
    b.addEventListener('click', () => { $('question-input').value = item.q; runAnalyst(item.q); });
    list.append(b);
  });
}
// P1-R1 Live latency UX: elapsed timer + truthful status
// No artificial client timeout — let genuine server/network/proxy failure terminate.
// Server may take several minutes for bounded Live lookback + env_params calls.
// User may explicitly cancel by switching mode or navigating away.
function startLiveTimer() { clearLiveTimer(); state.liveStart = Date.now(); state.liveTimer = setInterval(() => updateLiveProgress(), 1000); updateLiveProgress(); }
function clearLiveTimer() { if (state.liveTimer) { clearInterval(state.liveTimer); state.liveTimer = null; } state.liveStart = 0; }
function updateLiveProgress() {
  const elapsed = state.liveStart ? Math.round((Date.now() - state.liveStart) / 1000) : 0;
  const region = $('status-region');
  if (!region || !state.liveStart) return;
  // Truthful wording: describe what MAY be occurring, not synthetic stage transitions.
  const hint = elapsed < 5 ? 'Requesting FortyGuard evidence…'
    : elapsed < 60 ? 'Provider processing can take several minutes…'
    : 'Still waiting for the provider response…';
  region.replaceChildren();
  const s = document.createElement('span'); s.textContent = `${hint} `;
  const timer = document.createElement('strong'); timer.textContent = `${elapsed}s`;
  s.append(timer); region.append(s);
}
function init() { $('question-input').value = DEFAULT_QUESTION; initSourceControls(); initMap(); initHeatOpacityControl(); initBasemapControl(); initQuestionCatalogue(); $('question-form').addEventListener('submit', (e) => { e.preventDefault(); const q = $('question-input').value.trim(); if (q && q !== DEFAULT_QUESTION) runAnalyst(q); else request(state.mode); });   $('btn-replay').addEventListener('click', () => request('replay')); $('btn-live').addEventListener('click', () => request('live')); $('btn-unit').addEventListener('click', toggleUnit); $('map-focus-button').addEventListener('click', () => setFocusMode(!state.focusMode)); $('fit-area-button').addEventListener('click', fitMeasuredArea); $('focus-exit-button').addEventListener('click', () => setFocusMode(false)); document.addEventListener('keydown', handleEscape); $('evidence-close').addEventListener('click', () => { $('evidence-drawer').hidden = true; $('evidence-toggle').setAttribute('aria-expanded', 'false'); }); $('evidence-toggle').addEventListener('click', openEvidence); request('replay'); }
window.addEventListener('DOMContentLoaded', init);
