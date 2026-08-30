const DEFAULT_QUESTION = 'Where should Phoenix prioritize a cooling intervention this afternoon?';
const TIE_THRESHOLD = 0.1;
const state = { mode: 'replay', requestId: 0, requestGeneration: 0, controller: null, liveJobId: null, livePollTimer: null, map: null, resizeObserver: null, heatLayer: null, aoiLayer: null, highlightLayer: null, highlightRenderer: null, highlightCanvas: null, measuredAreaBounds: null, markers: new Map(), intersectionMarkers: new Map(), candidates: [], payload: null, replayEnv: null, focused: null, focusMode: false, focusScrollY: 0, evidenceAnimating: null, heatOpacity: 0.65, basemap: 'standard', liveStart: 0, liveTimer: null, unit: 'C' };
const deskState = { mode: 'replay', phase: 'idle', readout: 'status' };
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
const modeLabel = (mode) => mode === 'live' ? 'LIVE CONTEXT' : 'HISTORICAL OBSERVATION';

function initMap() {
  if (!window.L || state.map) return;
  state.map = L.map('map', { zoomControl: true, attributionControl: true, preferCanvas: true }).setView([33.4484, -112.074], 12);
  // OpenStreetMap is a no-key fallback; it keeps the demonstration free of API-key watermarks.
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19, attribution: '&copy; OpenStreetMap contributors' }).addTo(state.map);
  const container = $('map');
  if (window.ResizeObserver && container) {
    state.resizeObserver = new ResizeObserver(() => state.map?.invalidateSize({ pan: false }));
    state.resizeObserver.observe(container);
  }
}
function clearMap() {
  if (!state.map) return;
  if (state.evidenceAnimating) { clearTimeout(state.evidenceAnimating); state.evidenceAnimating = null; }
  window.__lunaState_evidenceAnimating = state.evidenceAnimating;
  if (state.heatLayer) { state.map.removeLayer(state.heatLayer); state.heatLayer = null; }
  if (state.aoiLayer) { state.map.removeLayer(state.aoiLayer); state.aoiLayer = null; }
  clearSourceCellHighlight();
  state.measuredAreaBounds = null;
  const areaLabel = $('measured-area-label');
  if (areaLabel) areaLabel.hidden = true;
  state.markers.forEach((m) => state.map.removeLayer(m));
  state.markers.clear();
  state.intersectionMarkers.forEach((m) => state.map.removeLayer(m));
  state.intersectionMarkers.clear();
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
   state.candidates = Array.isArray(payload.ranked_candidates) ? payload.ranked_candidates : [];
   state.candidates.forEach((candidate) => { addMarker(candidate); addIntersectionMarker(candidate); });
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
function addIntersectionMarker(candidate) { const intersection = candidate.candidate_context?.intersection; if (!state.map || !intersection?.available || !Array.isArray(intersection.coordinate)) return; const [lon, lat] = intersection.coordinate; if (!Number.isFinite(lat) || !Number.isFinite(lon)) return; const marker = L.marker([lat, lon], { icon: L.divIcon({ className: 'intersection-marker', html: '<div aria-hidden="true">○</div>', iconSize: [22, 22], iconAnchor: [11, 11] }), title: `${candidate.rank}: ${intersection.name || 'Road context'}`, zIndexOffset: -100 }).addTo(state.map); marker.bindTooltip(`Candidate ${candidate.rank} · ${intersection.name || 'Nearest intersection'} · ${intersection.distance_m ?? '—'} m`, { direction: 'top' }); marker.on('click', () => focusCandidate(candidate.rank, true)); state.intersectionMarkers.set(candidate.rank, marker); }
function addMarker(candidate) { if (!state.map || !Array.isArray(candidate.coordinate)) return; const [lon, lat] = candidate.coordinate; if (!Number.isFinite(lat) || !Number.isFinite(lon)) return; const peers = state.candidates.filter((c) => c !== candidate && Math.abs(c.coordinate?.[0] - lon) < 0.0005 && Math.abs(c.coordinate?.[1] - lat) < 0.0005); const fan = peers.length ? (Number(candidate.rank) - 2) * 15 : 0; const marker = L.marker([lat, lon], { icon: L.divIcon({ className: `candidate-marker marker-${candidate.rank}`, html: `<div style="display:grid;place-items:center;width:100%;height:100%;border-radius:50%;background:${candidate.rank === 1 ? 'var(--blue-dark)' : 'var(--blue)'};color:#fff;font:700 17px 'DM Mono',monospace;line-height:1;transform:translateX(${fan}px)">${candidate.rank}</div>`, iconSize: [42, 42], iconAnchor: [21, 21] }), title: `Candidate ${candidate.rank}`, riseOnHover: true, zIndexOffset: baseMarkerOffset(candidate.rank) }).addTo(state.map); marker.on('click', () => focusCandidate(candidate.rank, true)); state.markers.set(candidate.rank, marker); }
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
function focusCandidate(rank, pan = false) { state.focused = Number(rank) > 0 ? Number(rank) : null; document.querySelectorAll('.candidate-card').forEach((card) => card.classList.toggle('focused', Number(card.dataset.rank) === state.focused)); applyMarkerElevation(); highlightSourceCell(state.focused); const marker = state.markers.get(state.focused); if (marker && pan && state.map) state.map.flyTo(marker.getLatLng(), 16, { animate: !reducedMotion(), duration: 0.6 }); }
function clearSourceCellHighlight() {
  if (state.highlightLayer) {
    try { state.map.removeLayer(state.highlightLayer); } catch (e) { /* map may be mid-teardown */ }
    state.highlightLayer = null;
  }
  if (state.highlightRenderer) {
    try { state.map.removeLayer(state.highlightRenderer); } catch (e) { /* map may be mid-teardown */ }
    state.highlightRenderer = null;
  }
  if (state.highlightCanvas) { state.highlightCanvas.remove(); state.highlightCanvas = null; }
}
// Renderer-compatible source-cell highlight: the heat field uses Leaflet's Canvas
// renderer (preferCanvas:true), so cells have no per-feature DOM element. Apply a
// dedicated Canvas-rendered overlay for the candidate's true tile_id so the
// highlight is consumer-visible over the measured field without touching data or ranking.
function highlightSourceCell(rank) {
  clearSourceCellHighlight();
  if (!rank || !state.candidates.length || !state.map) return;
  const cand = state.candidates.find((c) => c.rank === Number(rank));
  if (!cand || !cand.tile_id) return;
  let feature = null;
  if (state.heatLayer) {
    state.heatLayer.eachLayer((layer) => {
      const f = layer.feature;
      if (f && f.properties && String(f.properties.tile_id) === String(cand.tile_id)) feature = f;
    });
  }
  if (!feature) return;
  const renderer = L.canvas();
  const layer = L.geoJSON(feature, {
    renderer,
    interactive: false,
    style: () => ({ color: '#d9871b', weight: 3, fillColor: '#ffb84d', fillOpacity: 0.3, dashArray: null, opacity: 1 })
  });
  renderer.addTo(state.map);
  layer.addTo(state.map);
  state.highlightLayer = layer;
  state.highlightRenderer = renderer;
  const canvas = (renderer.getContainer && renderer.getContainer())
    || (renderer.getCanvas && renderer.getCanvas())
    || renderer._container || null;
  if (canvas) {
    canvas.classList.add('source-cell-highlight');
    canvas.dataset.tileId = String(cand.tile_id);
    state.highlightCanvas = canvas;
  }
}
function parkLabel(parks) { if (!parks || parks.available === false) return 'Parks context unavailable'; if (parks.inside_park && typeof parks.inside_park === 'object') return `Inside mapped park${parks.inside_park.park_name ? `: ${parks.inside_park.park_name}` : ''}`; return 'No mapped park at candidate'; }
function removeReplayContext() { $('replay-env-context')?.remove(); }
function renderCandidates(payload) { const list = $('candidate-list'); list.replaceChildren(); const candidates = Array.isArray(payload?.ranked_candidates) ? payload.ranked_candidates : []; state.candidates = candidates; const status = payload?.conditions?.ranking_status; const explainer = $('candidate-explainer'); if (explainer) explainer.textContent = status === 'near_tie' ? 'Deterministic rank from the measured field. The hottest measured locations are nearly tied; context below is descriptive, not a score.' : 'Deterministic rank from the measured field. Context below is descriptive, not a score.'; if (!candidates.length) { const empty = document.createElement('p'); empty.className = 'empty-state'; empty.textContent = 'No candidate locations were returned for this mode.'; list.append(empty); return; }
  candidates.forEach((c) => { const card = document.createElement('article'); card.className = `candidate-card ${status === 'near_tie' ? 'near-tie' : ''}`; card.dataset.rank = c.rank; card.tabIndex = 0; card.setAttribute('aria-label', `Candidate ${c.rank}, ${tempD2(c.observed_temp)}`); card.addEventListener('mouseenter', () => focusCandidate(c.rank)); card.addEventListener('mouseleave', () => focusCandidate(-1)); card.addEventListener('focus', () => focusCandidate(c.rank)); card.addEventListener('click', () => focusCandidate(c.rank, true)); card.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); focusCandidate(c.rank, true); } });
    const eyebrow = document.createElement('span'); eyebrow.className = 'eyebrow'; eyebrow.textContent = status === 'near_tie' ? 'TOP THERMAL CLUSTER' : 'THERMAL CANDIDATE'; const h = document.createElement('h3'); h.textContent = `Candidate ${c.rank}`; const rank = document.createElement('span'); rank.className = 'rank'; rank.textContent = String(c.rank).padStart(2, '0'); const temp = document.createElement('div'); temp.className = 'temp'; temp.textContent = tempD2(c.observed_temp); const delta = document.createElement('div'); delta.className = 'delta'; delta.textContent = `${deltaD(c.delta_from_area_mean)} vs area mean`; const divider = document.createElement('hr'); divider.className = 'candidate-divider'; const details = document.createElement('div'); details.className = 'candidate-details'; [['Coordinates', coordLabel(c.coordinate)]].forEach(([label, value]) => { const box = document.createElement('div'); const s = document.createElement('span'); s.textContent = label; const strong = document.createElement('strong'); strong.textContent = value; box.append(s, strong); details.append(box); });     const note = document.createElement('p'); note.className = 'candidate-note'; note.textContent = state.mode === 'replay' ? (status === 'near_tie' ? 'The hottest measured locations are nearly tied; local context does not change the thermal ranking.' : 'Measured temperature plus local context; local context does not affect the thermal ranking.') : 'Thermal candidate identified from the measured field; local context does not alter the thermal ranking.';     const intersection = c.candidate_context?.intersection; if (intersection && intersection.available) { const intDiv = document.createElement('div'); intDiv.className = 'candidate-intersection'; intDiv.style.cssText = 'font-size:10px;color:var(--teal);margin-top:8px;padding-top:8px;border-top:1px solid var(--line);'; intDiv.textContent = `Nearest intersection: ${intersection.name || '—'} · ${intersection.distance_m != null ? intersection.distance_m + ' m' : '—'}`; card.append(eyebrow, h, rank, temp, delta, divider, details, note, intDiv); } else { const intDiv = document.createElement('div'); intDiv.className = 'candidate-intersection'; intDiv.style.cssText = 'font-size:10px;color:var(--muted,#94a3b8);margin-top:8px;padding-top:8px;border-top:1px solid var(--line);'; intDiv.textContent = 'Location context unavailable'; card.append(eyebrow, h, rank, temp, delta, divider, details, note, intDiv); } list.append(card); });
   renderIntersectionStates(candidates);
   if (state.mode === 'replay') renderRepresentativeContext();
  else removeReplayContext();
}
function renderIntersectionStates(candidates) {
  candidates.forEach((candidate) => {
    const intersection = candidate.candidate_context?.intersection;
    const card = document.querySelector(`.candidate-card[data-rank="${candidate.rank}"]`);
    if (!card || !intersection) return;
    let display = card.querySelector('.candidate-intersection');
    if (!display) {
      display = document.createElement('div');
      display.className = 'candidate-intersection';
      card.append(display);
    }
    if (intersection.available === true) {
      display.textContent = `Nearest intersection: ${intersection.name || '—'} · ${intersection.distance_m != null ? `${intersection.distance_m} m` : 'distance unavailable'}`;
    } else if (intersection.error === 'no_intersection_within_200m') {
      display.textContent = 'No mapped intersection within 200 m';
    } else if (String(intersection.error || '').startsWith('intersection_query_failed')) {
      display.textContent = 'Location context unavailable';
    } else {
      display.textContent = 'Location context unavailable';
    }
  });
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
function renderReadout() {
  const region = $('status-region');
  if (!region) return;
  region.replaceChildren();
  if (deskState.readout === 'analyst') return;
  const label = document.createElement('strong');
  label.textContent = deskState.phase === 'error' ? `${deskState.mode.toUpperCase()} UNAVAILABLE` : deskState.phase === 'ready' ? `DESK READOUT · ${deskState.mode.toUpperCase()}` : `DESK STATUS · ${deskState.mode.toUpperCase()}`;
  const detail = document.createElement('span');
  detail.textContent = deskState.phase === 'error' ? ' The current evidence request could not be completed.' : deskState.phase === 'ready' ? ` ${state.payload?.summary || 'Thermal evidence is ready for investigation.'}` : ` ${deskState.mode === 'replay' ? 'Loading deterministic local capture' : 'Requesting latest available provider observation'}…`;
  region.append(label, detail);
  if (deskState.phase === 'error' && deskState.mode === 'live') {
    const retry = document.createElement('button');
    retry.className = 'mode-button';
    retry.type = 'button';
    retry.textContent = 'Try Replay';
    retry.addEventListener('click', () => request('replay'));
    region.append(retry);
  }
  if (deskState.phase === 'loading') {
    const timer = document.createElement('strong');
    timer.id = 'desk-elapsed';
    timer.textContent = ` ${Math.round((Date.now() - state.liveStart) / 1000)}s`;
    region.append(timer);
  }
}
function clearResultSurfaces(message = 'Waiting for usable evidence.') {
  document.body.classList.remove('has-result');
  const railLabel = $('hero-context-label');
  if (railLabel) railLabel.textContent = modeLabel(state.mode);
  const railContent = $('hero-context-content');
  if (railContent) { railContent.replaceChildren(); const pending = document.createElement('span'); pending.textContent = state.mode === 'live' ? 'Live context pending — no Replay context retained.' : 'Replay context pending — no Live context retained.'; railContent.append(pending); }
  const identity = $('hero-identity');
  if (identity) identity.textContent = state.mode === 'live' ? 'Live workflow pending' : 'Replay capture pending';
  clearLiveTimer();
  state.payload = null;
  state.candidates = [];
  state.replayEnv = null;
  state.focused = null;
  removeReplayContext();
  clearMap();
  const nwsBanner = $('nws-forecast-banner');
  if (nwsBanner) { nwsBanner.hidden = true; nwsBanner.replaceChildren(); }
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
   clearResultSurfaces('Loading the decision…');
  text($('stat-obs-time'), 'Loading…');
  text($('observation-note'), message);
  text($('mode-badge'), mode.toUpperCase());
  $('mode-badge').className = `mode-badge ${mode}`;
  text($('map-source-label'), `FortyGuard · ${mode === 'replay' ? 'Replay' : 'Live'}`);
   text($('map-loading'), message);
   renderReadout();
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
function renderHeroContextRail(payload) {
  const ctxLabel = $('hero-context-label');
  const ctxContent = $('hero-context-content');
  const identity = $('hero-identity');
  if (!ctxContent || !identity) return;
  if (ctxLabel) ctxLabel.textContent = modeLabel(payload?.mode || state.mode);
  ctxContent.replaceChildren();
  const mode = payload?.mode || state.mode;
  if (mode === 'live') {
    if (ctxLabel) ctxLabel.textContent = 'NWS FORECAST';
    const nws = payload?.nws_context;
    const cond = nws?.conditions;
    if (cond) {
      const nwsTempC = cond.temperature_f != null ? (cond.temperature_f - 32) * 5 / 9 : null;
      const val = document.createElement('div'); val.className = 'nws-val';
      val.textContent = `${tempD(nwsTempC)} · ${cond.short_forecast || '—'}`;
      const detail = document.createElement('div'); detail.className = 'nws-detail';
      detail.textContent = `Wind: ${cond.wind_speed || '—'} ${cond.wind_direction || ''}`;
      ctxContent.append(val, detail);
    } else {
      const unavail = document.createElement('div'); unavail.textContent = 'Forecast unavailable';
      ctxContent.append(unavail);
    }
    if (nws?.alerts && nws.alerts.length > 0) {
      nws.alerts.forEach((a) => { const alert = document.createElement('div'); alert.className = 'nws-alert'; alert.textContent = `⚠ ${a.event || 'Alert'}`; ctxContent.append(alert); });
    }
    const disc = document.createElement('div'); disc.className = 'rail-disclosure'; disc.textContent = 'Supplemental · not used to rank';
    ctxContent.append(disc);
    identity.textContent = `Live observation · ${payload?.observation_time || 'pending'}`;
  } else {
    if (ctxLabel) ctxLabel.textContent = 'HISTORICAL OBSERVATION';
    const obs = payload?.historical_nws_obs;
    if (obs && obs.temperature?.value != null) {
      const val = document.createElement('div'); val.className = 'nws-val';
      val.textContent = `${tempD(obs.temperature.value)} · ${obs.text_description || '—'}`;
      const detail = document.createElement('div'); detail.className = 'nws-detail';
      detail.textContent = `Station: ${obs.station_identifier || 'KPHX'} · ${obs.observation_timestamp || '—'}`;
      ctxContent.append(val, detail);
    } else {
      const unavail = document.createElement('div'); unavail.textContent = 'Historical observation unavailable';
      ctxContent.append(unavail);
    }
    const ha = payload?.historical_alerts;
    const cp = ha?.consumer_projection;
    if (cp && cp.active_hazards && cp.active_hazards.length > 0) {
      const haz = document.createElement('div'); haz.className = 'nws-alert';
      haz.textContent = `Active: ${cp.active_hazards.map((h) => h.event).join(' and ')}`;
      ctxContent.append(haz);
    }
    const disc = document.createElement('div'); disc.className = 'rail-disclosure'; disc.textContent = 'Replay · not used to rank';
    ctxContent.append(disc);
    identity.textContent = `Replay capture · ${payload?.observation_time || 'Aug 25, 2026 14:00 MST'}`;
  }
}
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
  if (error) { deskState.phase = 'error'; deskState.readout = 'status'; renderError(payload, mode); renderReadout(); return; }
  document.body.classList.add('has-result');
  if (mode === 'live') renderNwsForecast(payload);
  else renderHistoricalNwsContext(payload);
  renderHeroContextRail(payload);
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
  deskState.phase = 'ready';
  deskState.readout = 'decision_summary';
  renderReadout();
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
const INTENT_ROUTES = [
  { id: 'mode', re: /show live data|use live|switch to live|show replay|use replay|switch to replay/ },
  { id: 'unsupported', re: /plant|planting|trees would|cool most|cooling effect|reduce|benefit most|how many degrees|work best|efficacy|intervention|what can this analysis not tell me/ },
  { id: 'canopy', re: /canopy|tree cover|trees/ },
  { id: 'parks', re: /near parks|parks/ },
  { id: 'map', re: /focus candidate|show candidate|focus the map|measured cell/ },
  { id: 'evidence', re: /evidence|provenance|data came|trust/ },
  { id: 'weather', re: /nws|weather|happening now|forecast/ },
  { id: 'tie', re: /nearly tied|tie|winner|close/ },
  { id: 'compare', re: /compare|different|candidates/ },
  { id: 'priority', re: /where|hottest|top locations|priorit/ }
];
function parseIntent(question) {
  const q = String(question || '').toLowerCase();
  for (const route of INTENT_ROUTES) {
    if (route.re.test(q)) {
      return INTENTS.find((intent) => intent.id === route.id) || INTENTS.find((intent) => intent.id === 'not_understood');
    }
  }
  return INTENTS.find((intent) => intent.id === 'not_understood');
}
function requestedMode(question) { return /\blive\b/i.test(question) ? 'live' : 'replay'; }
function runAnalyst(question) {
  const intent = parseIntent(question);
  const targetMode = intent.id === 'mode' ? requestedMode(question) : state.mode;
  const result = $('analyst-result'); result.replaceChildren();
  const answer = document.createElement('p'); answer.textContent = intent.answer(question, targetMode);
  const source = document.createElement('small'); source.textContent = `Source: ${intent.source} · Why it matters: ${intent.why || 'This source directly supports the answer.'}`;
  const readout = $('status-region');
  readout.replaceChildren();
  const label = document.createElement('strong'); label.textContent = `DESK READOUT · ${intent.id.toUpperCase()}`;
  readout.append(label, answer, source);
  deskState.readout = 'decision_summary';
  const suggestions = $('analyst-suggestions'); suggestions.replaceChildren();
  intent.suggestions.filter((s) => !(state.mode === 'replay' && /NWS|weather|current/i.test(s))).slice(0, 3).forEach((suggestion) => { const b = document.createElement('button'); b.type = 'button'; b.textContent = suggestion; b.addEventListener('click', () => { $('question-input').value = suggestion; runAnalyst(suggestion); }); suggestions.append(b); });
  intent.action?.();
  if (intent.id === 'mode') request(targetMode);
  // For not_understood: show the answer but do NOT trigger a request or mode switch
}
function openEvidence() { const drawer = $('evidence-drawer'); drawer.hidden = false; $('evidence-toggle').setAttribute('aria-expanded', 'true'); drawer.scrollIntoView({ behavior: scrollBehavior(), block: 'start' }); }
function setFocusMode(enabled) { if (enabled && !state.focusMode) state.focusScrollY = window.scrollY; state.focusMode = enabled; document.body.classList.toggle('map-focus', enabled); $('map-focus-button').textContent = enabled ? 'Exit map focus' : 'Focus map'; $('map-focus-button').setAttribute('aria-pressed', String(enabled)); const exitBtn = $('focus-exit-button'); if (exitBtn) { exitBtn.hidden = true; exitBtn.setAttribute('aria-pressed', 'false'); } if (enabled) $('map-focus-button').focus(); requestAnimationFrame(() => state.map?.invalidateSize({ pan: false })); if (!enabled) requestAnimationFrame(() => window.scrollTo({ top: state.focusScrollY, behavior: scrollBehavior() })); }
function toggleUnit() { state.unit = state.unit === 'C' ? 'F' : 'C'; $('btn-unit').textContent = state.unit === 'F' ? '°F ' : '°C '; const small = document.createElement('small'); small.textContent = state.unit === 'F' ? '/ °C' : '/ °F'; $('btn-unit').append(small); $('btn-unit').classList.toggle('active', state.unit === 'F'); $('btn-unit').setAttribute('aria-pressed', String(state.unit === 'F')); if (state.payload) render(state.payload, state.mode); }
async function request(mode = state.mode) {
  const id = ++state.requestId;
  state.requestGeneration = id;
  state.mode = mode;
  if (state.controller) state.controller.abort();
  state.controller = new AbortController();
  deskState.mode = mode; deskState.phase = 'loading'; deskState.readout = 'status';
  state.liveJobId = null;
  clearLiveTimer();
  setLoading(mode === 'replay' ? 'Loading reproducible capture…' : 'Requesting latest available provider observation…', mode);
  $('btn-replay').classList.toggle('active', mode === 'replay');
  $('btn-live').classList.toggle('active', mode === 'live');
  $('btn-replay').setAttribute('aria-pressed', String(mode === 'replay'));
  $('btn-live').setAttribute('aria-pressed', String(mode === 'live'));
  startLiveTimer();
  try {
    const q = $('question-input').value || DEFAULT_QUESTION;
    let payload;
    if (mode === 'live') {
      const start = await fetch('/api/live/start', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ question: q }), signal: state.controller.signal });
      const started = await start.json();
      if (!start.ok) throw new Error(started.message || `Server returned ${start.status}`);
      state.liveJobId = started.job_id;
      payload = await pollLiveJob(id, state.liveJobId, state.controller.signal);
    } else {
      const response = await fetch(`/api/answer?question=${encodeURIComponent(q)}&mode=replay`, { signal: state.controller.signal });
      try { payload = await response.json(); } catch { payload = { error: true, message: 'Invalid server response', mode }; }
      if (!response.ok) payload = { ...(payload || {}), error: true, mode };
    }
    if (id !== state.requestGeneration) return;
    clearLiveTimer();
    render(payload || { error: true, mode }, mode);
  } catch (error) {
    if (id !== state.requestGeneration) return;
    clearLiveTimer();
    if (error.name !== 'AbortError') {
      clearResultSurfaces(mode === 'live' ? 'Live evidence unavailable.' : 'Replay evidence unavailable.');
      deskState.phase = 'error'; deskState.readout = 'status';
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
      renderReadout();
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
const CATALOGUE_GROUPS = {
  decision: ['priority', 'compare', 'tie'],
  context: ['weather', 'canopy', 'parks'],
  evidence: ['evidence', 'unsupported', 'map']
};
function initQuestionCatalogue() {
  const toggle = document.querySelector('.catalogue-toggle');
  const panel = $('catalogue-panel');
  if (!toggle || !panel) return;
   const desktopExpanded = window.innerWidth >= 1050;
   toggle.setAttribute('aria-expanded', String(desktopExpanded));
   panel.hidden = !desktopExpanded;
   window.addEventListener('resize', () => {
     if (window.innerWidth < 700) {
       toggle.setAttribute('aria-expanded', 'false');
       panel.hidden = true;
     } else if (window.innerWidth >= 1050) {
       toggle.setAttribute('aria-expanded', 'true');
       panel.hidden = false;
     }
   });
   toggle.addEventListener('click', () => {
    const expanded = toggle.getAttribute('aria-expanded') === 'true';
    toggle.setAttribute('aria-expanded', String(!expanded));
    panel.hidden = expanded;
  });
  Object.entries(CATALOGUE_GROUPS).forEach(([groupId, intentIds]) => {
    const container = $(`catalogue-${groupId}`);
    if (!container) return;
    container.replaceChildren();
    CATALOGUE_QUESTIONS.filter((item) => intentIds.some((id) => item.intents.includes(id))).forEach((item) => {
      const b = document.createElement('button');
      b.type = 'button';
      b.textContent = item.q;
      b.addEventListener('click', () => { $('question-input').value = item.q; runAnalyst(item.q); });
      container.append(b);
    });
  });
}
// P1-R1 Live latency UX: elapsed timer + truthful status
// No artificial client timeout — let genuine server/network/proxy failure terminate.
// Server may take several minutes for bounded Live lookback + env_params calls.
// User may explicitly cancel by switching mode or navigating away.
function startLiveTimer() { clearLiveTimer(); state.liveStart = Date.now(); state.liveTimer = setInterval(() => updateLiveProgress(), 1000); updateLiveProgress(); }
function clearLiveTimer() { if (state.liveTimer) { clearInterval(state.liveTimer); state.liveTimer = null; } if (state.livePollTimer) { clearTimeout(state.livePollTimer); state.livePollTimer = null; } state.liveStart = 0; }
function updateLiveProgress() {
  const elapsed = state.liveStart ? Math.round((Date.now() - state.liveStart) / 1000) : 0;
  if (!state.liveStart || deskState.phase !== 'loading') return;
  renderReadout();
}
async function pollLiveJob(id, jobId, signal) {
  while (id === state.requestGeneration && state.liveJobId === jobId) {
    const response = await fetch(`/api/live/status?job_id=${encodeURIComponent(jobId)}`, { signal });
    const status = await response.json();
    if (!response.ok) throw new Error(status.message || `Server returned ${response.status}`);
    text($('observation-note'), status.stage ? `${titleCase(status.stage)} · ${status.elapsed_seconds ?? 0}s` : 'Live provider workflow in progress…');
    if (status.state === 'completed') return status.payload;
    if (status.state === 'failed') return status.payload || { error: true, mode: 'live', message: 'Live job failed.' };
    await new Promise((resolve) => { state.livePollTimer = setTimeout(resolve, 800); });
  }
  throw new DOMException('Stale Live request', 'AbortError');
}

function init() { $('question-input').value = DEFAULT_QUESTION; initSourceControls(); initMap(); initHeatOpacityControl(); initBasemapControl(); initQuestionCatalogue(); $('question-form').addEventListener('submit', (e) => { e.preventDefault(); const q = $('question-input').value.trim(); if (q && q !== DEFAULT_QUESTION) runAnalyst(q); else request(state.mode); });   $('btn-replay').addEventListener('click', () => request('replay')); $('btn-live').addEventListener('click', () => request('live')); $('btn-unit').addEventListener('click', toggleUnit); $('map-focus-button').addEventListener('click', () => setFocusMode(!state.focusMode)); $('fit-area-button').addEventListener('click', fitMeasuredArea); $('focus-exit-button').addEventListener('click', () => setFocusMode(false)); document.addEventListener('keydown', handleEscape); $('evidence-close').addEventListener('click', () => { $('evidence-drawer').hidden = true; $('evidence-toggle').setAttribute('aria-expanded', 'false'); }); $('evidence-toggle').addEventListener('click', openEvidence); request('replay'); }
window.addEventListener('DOMContentLoaded', init);
