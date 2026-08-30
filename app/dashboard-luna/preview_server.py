"""Same-origin Luna preview server.

Run from repository root:
    python3 app/dashboard-luna/preview_server.py
"""
import json
import os
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
sys.path.insert(0, str(REPO))
from app.server import build_visualization_payload, get_agent_result, build_identity  # noqa: E402

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def _json(self, status, payload):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/answer":
            params = parse_qs(parsed.query)
            question = params.get("question", ["Where should Phoenix prioritize a cooling intervention this afternoon?"])[0]
            mode = params.get("mode", ["replay"])[0]
            if mode not in ("replay", "live"):
                self._json(400, {"error": True, "message": "Invalid mode"})
                return
            try:
                self._json(200, build_visualization_payload(get_agent_result(question, mode)))
            except Exception:
                self._json(500, {"error": True, "mode": mode, "message": "Unable to complete query"})
            return
        if parsed.path == "/api/config":
            self._json(200, {"carto_basemap_key": os.environ.get("CARTO_BASEMAP_KEY", "")})
            return
        if parsed.path == "/":
            index = (ROOT / "index.html").read_text()
            build_version = build_identity()
            body = index.replace("{{BUILD_VERSION}}", build_version).encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Cache-Control", "no-cache, must-revalidate")
            self.end_headers()
            self.wfile.write(body)
            return
        return super().do_GET()

if __name__ == "__main__":
    port = int(os.environ.get("LUNA_PORT", "8090"))
    print(f"Luna same-origin preview: http://localhost:{port}/")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
