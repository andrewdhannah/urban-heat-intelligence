"""
S2 Application Server — Decision Experience

Serves the browser application and provides API endpoints
for the HeatAgent in both LIVE and REPLAY modes.
"""

import json
import sys
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.agent.adapter import FortyGuardAdapter
from src.agent.controller import HeatAgent


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

    # Get NWS corroboration context
    nws_context = None
    try:
        from src.tools.nws import get_nws_context
        nws_context = get_nws_context()
    except Exception:
        pass

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
        "evidence_chain": chain,
        "error": answer.get("error", False)
    }


class UHIHandler(SimpleHTTPRequestHandler):
    """Serve static files and API endpoints."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(Path(__file__).parent / "static"), **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/":
            self.serve_index()
        elif parsed.path == "/api/answer":
            params = parse_qs(parsed.query)
            question = params.get("question", ["Where should Phoenix prioritize a cooling intervention this afternoon?"])[0]
            mode = params.get("mode", ["replay"])[0]
            self.serve_answer(question, mode)
        elif parsed.path == "/api/nws":
            self.serve_nws()
        else:
            super().do_GET()

    def serve_index(self):
        index_path = Path(__file__).parent / "static" / "index.html"
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
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(response.encode())
        except Exception as e:
            error = json.dumps({"error": True, "message": str(e), "mode": mode})
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(error.encode())

    def serve_nws(self):
        try:
            from src.tools.nws import get_nws_context
            nws_data = get_nws_context()
            response = json.dumps(nws_data)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(response.encode())
        except Exception as e:
            error = json.dumps({"error": True, "message": str(e)})
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(error.encode())


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
