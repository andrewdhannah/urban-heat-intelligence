"""
S2 Application Server — Decision Experience

Serves the browser application and provides API endpoints
for the HeatAgent in both LIVE and REPLAY modes.
"""

import json
import os
import sys
import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

ALLOWED_VARIANTS = ("incumbent", "luna")
DEFAULT_VARIANT = "luna"
LIVE_MAX_ACTIVE = 1
LIVE_JOB_TTL_SECONDS = 30 * 60
LIVE_JOBS = {}
LIVE_JOBS_LOCK = threading.RLock()
LIVE_SLOT = threading.BoundedSemaphore(LIVE_MAX_ACTIVE)


def build_identity():
    return os.environ.get("RENDER_GIT_COMMIT") or os.environ.get("GIT_COMMIT") or "local-dev"


def _cleanup_live_jobs(now=None):
    now = now or time.time()
    with LIVE_JOBS_LOCK:
        expired = [job_id for job_id, job in LIVE_JOBS.items()
                   if job["state"] in ("completed", "failed") and now - job["finished_at"] > LIVE_JOB_TTL_SECONDS]
        for job_id in expired:
            LIVE_JOBS.pop(job_id, None)


def _set_live_job(job_id, **updates):
    with LIVE_JOBS_LOCK:
        job = LIVE_JOBS.get(job_id)
        if job:
            job.update(updates)
            job["updated_at"] = time.time()


def _run_live_job(job_id, question):
    if not LIVE_SLOT.acquire(blocking=False):
        _set_live_job(job_id, state="failed", stage="capacity", safe_error_class="capacity_exhausted", finished_at=time.time())
        return
    try:
        _set_live_job(job_id, state="running", stage="fortyguard_workflow", provider_operation="heatmap_and_environmental_parameters")
        result = get_agent_result(question, "live")
        payload = build_visualization_payload(result)
        if payload.get("error"):
            _set_live_job(job_id, state="failed", stage="provider_result", safe_error_class="provider_unavailable", payload=payload, finished_at=time.time())
        else:
            _set_live_job(job_id, state="completed", stage="complete", payload=payload, finished_at=time.time())
    except Exception as exc:
        print(f"[ERROR] live job failed: {type(exc).__name__}", file=sys.stderr)
        _set_live_job(job_id, state="failed", stage="worker", safe_error_class=type(exc).__name__, finished_at=time.time())
    finally:
        LIVE_SLOT.release()


def get_dashboard_variant():
    """Read the controlled dashboard variant from the environment.

    UHI_DASHBOARD_VARIANT controls which presentation layer is served.
    Allowed values: incumbent, luna.  Invalid values fall back to incumbent.
    The API backend is shared regardless of variant.
    """
    variant = os.environ.get("UHI_DASHBOARD_VARIANT", DEFAULT_VARIANT).lower().strip()
    return variant if variant in ALLOWED_VARIANTS else DEFAULT_VARIANT


def get_dashboard_dir():
    """Return the Path to the static directory for the active variant."""
    variant = get_dashboard_variant()
    if variant == "luna":
        return Path(__file__).parent / "dashboard-luna"
    return Path(__file__).parent / "static"

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.agent.adapter import FortyGuardAdapter
from src.agent.controller import HeatAgent
from src.agent.brief import compose_urban_heat_brief


def get_agent_result(question, mode="replay"):
    """Run the agent and return structured result for the UI."""
    adapter = FortyGuardAdapter(mode=mode)
    agent = HeatAgent(adapter, mode=mode)
    result = agent.answer(question)
    return result


def build_visualization_payload(result):
    """
    Build sanitized visualization payload for the browser.

    Visualization contract: each field derives from the SAME mode's data.
    No cross-mode fallback is permitted. If a mode's data is unavailable,
    the field is explicitly null — replay geometry is never substituted
    for live data, and vice versa.

    Contains only what the UI needs for rendering.
    No credentials, no raw provider internals.
    """
    answer = result.get("answer", {})
    chain = result.get("evidence_chain", [])
    raw = result.get("raw_results", {})
    mode = answer.get("mode", "unknown")

    # Extract heatmap features from the SAME mode's raw result only
    heatmap_features = []
    heatmap_obs_time = None
    hottest = None
    visualization_source = mode  # Explicit: visualization derives from this mode

    heatmap_result_raw = raw.get("heatmap", {})
    if heatmap_result_raw:
        # Verify the heatmap result's mode matches the answer mode
        heatmap_mode = heatmap_result_raw.get("mode")
        if heatmap_mode == mode:
            map_data = heatmap_result_raw.get("result", {}).get("map_data", {})
            heatmap_features = map_data.get("features", [])
            heatmap_obs_time = heatmap_result_raw.get("observation_time")
            hottest = heatmap_result_raw.get("hottest_feature")
        # If modes don't match, leave visualization fields empty — never cross-contaminate

    # Get env_params data from chain (chain nodes are mode-stamped)
    env_data = {}
    for node in chain:
        if node["step"] == "env_params_result":
            env_data = node["data"]
            break

    # Get coordinate selection from chain
    coord_data = {}
    for node in chain:
        if node["step"] == "coordinate_selection":
            coord_data = node["data"]
            break

    # Get ranked candidates from conditions
    ranked_candidates = answer.get("conditions", {}).get("ranked_candidates", [])

    # Get NWS corroboration context — LIVE only, never in REPLAY.
    # The same context is passed to the Brief and represented by explicit
    # supplemental evidence nodes; NWS never determines thermal ranking.
    nws_context = None
    heatmap_available = bool(heatmap_result_raw and heatmap_result_raw.get("result", {}).get("feature_count"))
    if mode == "live" and not answer.get("error") and heatmap_available:
        try:
            from src.tools.nws import get_nws_context
            nws_context = get_nws_context()
        except Exception:
            nws_context = None
        if nws_context is None:
            nws_context = {
                "provider": "NWS",
                "mode": "live",
                "conditions": None,
                "alerts": [],
                "alert_count": 0,
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
                "source_endpoints": [
                    "/gridpoints/PSR/128,48/forecast",
                    "/alerts/active?point=33.45,-112.07"
                ],
                "used_in_decision": False,
                "evidence_status": "unavailable"
            }
        else:
            nws_context["mode"] = "live"
            nws_context["used_in_decision"] = False
            nws_context["evidence_status"] = (
                "supplemental_context"
                if nws_context.get("conditions") or nws_context.get("alerts")
                else "unavailable"
            )
    elif mode == "live":
        # Do not fetch optional NWS context when FortyGuard has already
        # failed or returned no usable features.
        nws_context = {
            "provider": "NWS",
            "mode": "live",
            "conditions": None,
            "alerts": [],
            "alert_count": 0,
            "used_in_decision": False,
            "evidence_status": "not_requested_fortyguard_unavailable",
            "source_endpoints": []
        }
    else:
        nws_context = {
            "provider": "NWS",
            "mode": "replay",
            "conditions": None,
            "alerts": [],
            "alert_count": 0,
            "has_extreme_heat_warning": False,
            "used_in_decision": False,
            "evidence_status": "excluded_from_replay",
            "source_endpoints": [],
            "message": "NWS current context not included in historical Replay"
        }

    payload_chain = list(chain)
    if mode == "live" and nws_context.get("evidence_status") != "not_requested_fortyguard_unavailable":
        payload_chain.extend([
            {
                "step": "nws_request",
                "data": {
                    "provider": "NWS",
                    "mode": "live",
                    "endpoints": nws_context.get("source_endpoints", []),
                    "used_in_decision": False
                },
                "timestamp": nws_context.get("retrieved_at")
            },
            {
                "step": "nws_result",
                "data": {
                    "provider": "NWS",
                    "mode": "live",
                    "retrieved_at": nws_context.get("retrieved_at"),
                    "effective_start": (nws_context.get("conditions") or {}).get("effective_start"),
                    "effective_end": (nws_context.get("conditions") or {}).get("effective_end"),
                    "alert_count": nws_context.get("alert_count", 0),
                    "available": bool(nws_context.get("conditions") or nws_context.get("alerts")),
                    "used_in_decision": False
                },
                "timestamp": nws_context.get("retrieved_at")
            }
        ])
    else:
        payload_chain.append({
            "step": "nws_context",
            "data": {
                "provider": "NWS",
                "mode": "replay",
                "reason": "Current NWS forecast data excluded from Replay; frozen contemporaneous historical station observation and alert context included",
                "used_in_decision": False
            },
            "timestamp": None
        })

    urban_heat_brief = compose_urban_heat_brief(result, nws_context)
    if urban_heat_brief:
        payload_chain.append({
            "step": "brief",
            "data": {
                "title": urban_heat_brief["title"],
                "mode": urban_heat_brief["mode"],
                "claim_count": len(urban_heat_brief["claims"]),
                "source_providers": [source["provider"] for source in urban_heat_brief["sources"]],
                "ranking_status": urban_heat_brief["ranking_status"]
            },
            "timestamp": urban_heat_brief.get("generated_at")
        })

    # Add GIS context to payload (composition, not modification of thermal chain)
    gis_context = result.get("context", {})
    candidate_contexts = result.get("candidate_contexts", {})
    context_evidence_chain = result.get("context_evidence_chain", [])
    
    # Merge per-candidate GIS context into ranked_candidates
    for i, cand in enumerate(ranked_candidates):
        ctx = candidate_contexts.get(i, {})
        canopy = ctx.get("canopy")
        parks = ctx.get("parks")
        intersection = ctx.get("intersection")
        cand["candidate_context"] = {
            "canopy": {
                "available": canopy.get("available", False) if canopy else False,
                "census_tract_geoid": canopy.get("census_tract_geoid") if canopy else None,
                "tree_canopy_pct": canopy.get("tree_canopy_pct") if canopy else None,
                "reference_period": canopy.get("reference_period") if canopy else None,
                "source_provider": canopy.get("source_provider") if canopy else None,
            } if canopy else None,
            "parks": {
                "available": parks.get("available", False) if parks else False,
                "inside_park": parks.get("inside_park") if parks else None,
                "source_provider": parks.get("source_provider") if parks else None,
            } if parks else None,
            "intersection": {
                "available": intersection.get("available", False) if intersection else False,
                "name": intersection.get("name") if intersection else None,
                "distance_m": intersection.get("distance_m") if intersection else None,
                "source_provider": intersection.get("source_provider") if intersection else None,
                "used_in_decision": False,
            } if intersection else None,
            "used_in_decision": False,
        }
    
    # Add context evidence chain to payload
    if context_evidence_chain:
        payload_chain.extend(context_evidence_chain)

    # B1: Historical NWS station observation for Replay (fixture only, no network)
    historical_nws_obs = None
    if mode == "replay":
        obs_path = Path("fixtures/nws-historical/kphx-observation-aug25-14h.json")
        if obs_path.exists():
            try:
                with open(obs_path) as f:
                    obs_data = json.load(f)
                obs = obs_data.get("observation", {})
                historical_nws_obs = {
                    "provider": "NWS",
                    "mode": "replay",
                    "data_type": "station_observation",
                    "station_identifier": obs_data.get("station_metadata", {}).get("station_identifier"),
                    "station_name": obs_data.get("station_metadata", {}).get("station_name"),
                    "observation_timestamp": obs.get("timestamp"),
                    "target_time_local": obs_data.get("query", {}).get("target_time_local"),
                    "offset_minutes": obs_data.get("query", {}).get("offset_minutes"),
                    "temperature": obs.get("temperature"),
                    "dewpoint": obs.get("dewpoint"),
                    "wind_speed": obs.get("wind_speed"),
                    "wind_direction": obs.get("wind_direction"),
                    "relative_humidity": obs.get("relative_humidity"),
                    "barometric_pressure": obs.get("barometric_pressure"),
                    "visibility": obs.get("visibility"),
                    "heat_index": obs.get("heat_index"),
                    "text_description": obs.get("text_description", ""),
                    "used_in_decision": False,
                    "evidence_status": "historical_context",
                    "provenance": obs_data.get("provenance", {})
                }
                payload_chain.append({
                    "step": "historical_nws_observation",
                    "data": {
                        "provider": "NWS",
                        "mode": "replay",
                        "station": obs_data.get("query", {}).get("station"),
                        "offset_minutes": obs_data.get("query", {}).get("offset_minutes"),
                        "used_in_decision": False
                    },
                    "timestamp": obs.get("timestamp")
                })
            except Exception:
                historical_nws_obs = None

    # B3: Add historical alerts for Replay mode (fixture only, no network)
    historical_alerts = None
    if mode == "replay":
        alerts_path = Path("fixtures/nws-historical/phoenix-aug25-alerts.json")
        if alerts_path.exists():
            try:
                with open(alerts_path) as f:
                    alerts_data = json.load(f)
                historical_alerts = {
                    "provider": "NWS",
                    "mode": "replay",
                    "data_type": "historical_alerts",
                    "alerts": alerts_data.get("aug25_alerts", []),
                    "consumer_projection": alerts_data.get("consumer_projection"),
                    "query_time": alerts_data.get("query", {}).get("target_time_local"),
                    "used_in_decision": False,
                    "evidence_status": "historical_context",
                    "provenance": alerts_data.get("provenance", {})
                }
                payload_chain.append({
                    "step": "historical_alerts",
                    "data": {
                        "provider": "NWS",
                        "mode": "replay",
                        "alert_count": len(alerts_data.get("aug25_alerts", [])),
                        "used_in_decision": False
                    },
                    "timestamp": alerts_data.get("query", {}).get("retrieved_at")
                })
            except Exception:
                historical_alerts = None

    return {
        "mode": mode,
        "visualization_source": visualization_source,
        "observation_time": answer.get("observation_time"),
        "summary": answer.get("summary"),
        "conditions": answer.get("conditions"),
        "why_this_answer": answer.get("why_this_answer"),
        "sources": answer.get("sources"),
        "heatmap": {
            "features": heatmap_features,
            "observation_time": heatmap_obs_time,
            "feature_count": len(heatmap_features),
            "source": visualization_source
        },
        "priority_location": {
            "coordinate": hottest.get("coordinate") if hottest else None,
            "temperature": hottest.get("temperature_celsius") if hottest else None,
            "selection_method": hottest.get("selection_method") if hottest else None,
            "source": visualization_source,
            "env_params": {
                "heat_index": env_data.get("heat_index"),
                "apparent_temp": env_data.get("apparent_temp"),
                "humidity": env_data.get("humidity")
            }
        },
        "ranked_candidates": ranked_candidates,
        "nws_context": nws_context,
        "gis_context": gis_context,
        "historical_nws_obs": historical_nws_obs,
        "historical_alerts": historical_alerts,
        "urban_heat_brief": urban_heat_brief,
        "evidence_chain": payload_chain,
        "error": answer.get("error", False)
    }


class UHIHandler(SimpleHTTPRequestHandler):
    """Serve static files and API endpoints."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(get_dashboard_dir()), **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/":
            self.serve_index()
        elif parsed.path == "/api/live/status":
            self.serve_live_status(parse_qs(parsed.query).get("job_id", [""])[0])
        elif parsed.path == "/api/answer":
            params = parse_qs(parsed.query)
            question = params.get("question", ["Where should Phoenix prioritize a cooling intervention this afternoon?"])[0]
            mode = params.get("mode", ["replay"])[0]
            # Mode allowlist: only "replay" and "live" are valid
            if mode not in ("replay", "live"):
                self.send_error(400, "Invalid mode. Allowed: replay, live")
                return
            if mode == "live":
                self.write_json({"error": True, "mode": "live", "message": "Live queries must use POST /api/live/start and poll /api/live/status."}, status=400)
                return
            self.serve_answer(question, mode)
        elif parsed.path == "/api/nws":
            self.serve_nws()
        elif parsed.path == "/api/config":
            self.serve_config()
        elif parsed.path == "/api/variant":
            self.serve_variant()
        elif parsed.path == "/api/version":
            self.serve_version()
        else:
            if "v=" in parsed.query:
                self.serve_versioned_asset(parsed)
            else:
                super().do_GET()

    def serve_versioned_asset(self, parsed):
        """Serve a versioned static asset with immutable cache headers.

        Reads the file directly and writes a single HTTP response to avoid
        the double-header bug that occurs when super().do_GET() is called
        after headers are already sent.
        """
        asset_path = get_dashboard_dir() / parsed.path.lstrip("/")
        if not asset_path.exists():
            self.send_error(404, "Asset not found")
            return
        content = asset_path.read_bytes()
        content_type = self.guess_type(str(asset_path))
        build_version = os.environ.get("RENDER_GIT_COMMIT", "r6-dev")
        requested_version = parse_qs(parsed.query).get("v", [""])[0]
        if requested_version != build_version:
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Cache-Control", "no-cache, must-revalidate")
            self.send_header("X-Build-Version", build_version)
            self.end_headers()
            self.wfile.write(content)
            return
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "public, max-age=31536000, immutable")
        self.send_header("X-Build-Version", build_version)
        self.end_headers()
        self.wfile.write(content)

    def serve_index(self):
        index_path = get_dashboard_dir() / "index.html"
        build_version = os.environ.get("RENDER_GIT_COMMIT", "r6-dev")
        content = index_path.read_text().replace("{{BUILD_VERSION}}", build_version).encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Cache-Control", "no-cache, must-revalidate")
        self.end_headers()
        self.wfile.write(content)

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/api/live/start":
            self.send_error(404, "Not found")
            return
        length = int(self.headers.get("Content-Length", "0"))
        try:
            body = json.loads(self.rfile.read(min(length, 10000)) or b"{}")
        except (ValueError, UnicodeDecodeError):
            self.send_error(400, "Invalid JSON")
            return
        question = str(body.get("question") or "Where should Phoenix prioritize a cooling intervention this afternoon?")[:1000]
        _cleanup_live_jobs()
        with LIVE_JOBS_LOCK:
            active = sum(job["state"] in ("queued", "running") for job in LIVE_JOBS.values())
            if active >= LIVE_MAX_ACTIVE:
                self.write_json({"error": True, "message": "A Live request is already in progress."}, 429)
                return
            job_id = uuid.uuid4().hex
            LIVE_JOBS[job_id] = {"job_id": job_id, "state": "queued", "stage": "queued", "provider_operation": None,
                                 "safe_error_class": None, "created_at": time.time(), "updated_at": time.time(), "finished_at": None, "payload": None}
        threading.Thread(target=_run_live_job, args=(job_id, question), daemon=True, name=f"uhi-live-{job_id[:8]}").start()
        self.write_json({"job_id": job_id, "state": "queued"}, status=202)

    def write_json(self, value, status=200):
        response = json.dumps(value)
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(response.encode())

    def serve_live_status(self, job_id):
        _cleanup_live_jobs()
        with LIVE_JOBS_LOCK:
            job = LIVE_JOBS.get(job_id)
            if not job:
                self.write_json({"error": True, "message": "Live job not found."}, status=404)
                return
            response = {key: value for key, value in job.items() if key not in ("payload", "created_at", "updated_at", "finished_at")}
            response["elapsed_seconds"] = round((job["finished_at"] or time.time()) - job["created_at"], 1)
            if job["state"] in ("completed", "failed") and job.get("payload") is not None:
                response["payload"] = job["payload"]
        self.write_json(response)

    def serve_answer(self, question, mode):
        try:
            result = get_agent_result(question, mode)
            payload = build_visualization_payload(result)
            response = json.dumps(payload)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(response.encode())
        except Exception as e:
            # Bounded public error — no stack traces, no credential exposure
            error = json.dumps({"error": True, "message": "Unable to complete query", "mode": mode})
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(error.encode())
            # Server-side diagnostic logging (no credentials)
            import sys
            print(f"[ERROR] {mode} query failed: {type(e).__name__}", file=sys.stderr)

    def serve_nws(self):
        try:
            from src.tools.nws import get_nws_context
            nws_data = get_nws_context()
            response = json.dumps(nws_data)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(response.encode())
        except Exception as e:
            error = json.dumps({"error": True, "message": "Unable to fetch weather context"})
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(error.encode())

    def serve_config(self):
        """Return non-sensitive client configuration."""
        carto_key = os.environ.get("CARTO_BASEMAP_KEY", "")
        config = {
            "carto_basemap_key": carto_key
        }
        response = json.dumps(config)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(response.encode())

    def serve_variant(self):
        """Return the selected dashboard variant. No secrets exposed."""
        response = json.dumps({"variant": get_dashboard_variant()})
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(response.encode())

    def serve_version(self):
        """Return actual non-secret deployment identity."""
        self.write_json({"version": build_identity(), "build": build_identity(), "commit": build_identity()})


def main():
    import os
    port = int(os.environ.get("PORT", 8080))
    host = os.environ.get("HOST", "0.0.0.0")
    server = ThreadingHTTPServer((host, port), UHIHandler)
    print(f"Urban Heat Intelligence — Decision Experience")
    print(f"Running at http://localhost:{port}")
    print(f"Open in browser to use the application")
    server.serve_forever()


if __name__ == "__main__":
    main()
