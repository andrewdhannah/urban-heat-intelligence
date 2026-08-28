"""
S2 Application Server — Decision Experience

Serves the browser application and provides API endpoints
for the HeatAgent in both LIVE and REPLAY modes.
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

ALLOWED_VARIANTS = ("incumbent", "luna")
DEFAULT_VARIANT = "incumbent"


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
            "step": "nws_exclusion",
            "data": {
                "provider": "NWS",
                "mode": "replay",
                "reason": "Current NWS context is not included in historical Replay",
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
            "used_in_decision": False,
        }
    
    # Add context evidence chain to payload
    if context_evidence_chain:
        payload_chain.extend(context_evidence_chain)

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
        elif parsed.path == "/api/answer":
            params = parse_qs(parsed.query)
            question = params.get("question", ["Where should Phoenix prioritize a cooling intervention this afternoon?"])[0]
            mode = params.get("mode", ["replay"])[0]
            # Mode allowlist: only "replay" and "live" are valid
            if mode not in ("replay", "live"):
                self.send_error(400, "Invalid mode. Allowed: replay, live")
                return
            self.serve_answer(question, mode)
        elif parsed.path == "/api/nws":
            self.serve_nws()
        elif parsed.path == "/api/config":
            self.serve_config()
        elif parsed.path == "/api/variant":
            self.serve_variant()
        else:
            super().do_GET()

    def serve_index(self):
        index_path = get_dashboard_dir() / "index.html"
        content = index_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(content)

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


def main():
    import os
    port = int(os.environ.get("PORT", 8080))
    host = os.environ.get("HOST", "0.0.0.0")
    server = HTTPServer((host, port), UHIHandler)
    print(f"Urban Heat Intelligence — Decision Experience")
    print(f"Running at http://localhost:{port}")
    print(f"Open in browser to use the application")
    server.serve_forever()


if __name__ == "__main__":
    main()
