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
        elif parsed.path == "/api/fixture":
            params = parse_qs(parsed.query)
            name = params.get("name", ["heatmap"])[0]
            self.serve_fixture(name)
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
            # Remove raw_results to keep response size reasonable
            if "raw_results" in result:
                del result["raw_results"]
            response = json.dumps(result)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(response.encode())
        except Exception as e:
            error = json.dumps({"error": str(e)})
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(error.encode())

    def serve_fixture(self, name):
        fixture_map = {
            "heatmap": "fixtures/fortyguard/heatmap/phoenix-2026-08-25-14h.json",
            "env_params": "fixtures/fortyguard/env_params/phoenix-33.4484--112.0740-2026-08-25-14h.json",
        }
        fixture_path = Path(__file__).resolve().parent.parent / fixture_map.get(name, "")
        if fixture_path.exists():
            content = fixture_path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(content)
        else:
            self.send_response(404)
            self.end_headers()


def main():
    port = 8080
    server = HTTPServer(("127.0.0.1", port), UHIHandler)
    print(f"Urban Heat Intelligence — Decision Experience")
    print(f"Running at http://localhost:{port}")
    print(f"Open in browser to use the application")
    server.serve_forever()


if __name__ == "__main__":
    main()
