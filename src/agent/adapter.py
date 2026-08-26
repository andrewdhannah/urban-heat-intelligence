"""
FortyGuard Adapter — S1 wrapper around minimal S0 adapter

Provides submit_heatmap, submit_env_params, poll_status methods.
"""

import json
import ssl
import time
import urllib.request
import urllib.error
from pathlib import Path

BASE_URL = "https://api.fortyguard.com/v1"


def _make_ssl_context():
    """Create SSL context — unverified for hackathon API compatibility."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


class FortyGuardAdapter:
    """FortyGuard API adapter with live and replay capabilities."""

    def __init__(self, api_key=None, mode="live"):
        self.mode = mode
        if api_key:
            self.api_key = api_key
        elif mode == "live":
            self.api_key = self._load_api_key()
        else:
            self.api_key = None
        self._ssl_ctx = _make_ssl_context()

    def _load_api_key(self):
        """Load from governed secret store."""
        env_path = Path(__file__).resolve().parent.parent.parent / ".secrets" / "fortyguard.env"
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("FORTYGUARD_API_KEY="):
                    return line.split("=", 1)[1].strip()
        raise RuntimeError("FORTYGUARD_API_KEY not found")

    def _make_request(self, method, path, body=None):
        """Make authenticated request."""
        url = f"{BASE_URL}{path}"
        req = urllib.request.Request(url, method=method)
        req.add_header("api-key", self.api_key)
        req.add_header("Content-Type", "application/json")
        if body:
            req.data = json.dumps(body).encode()
        with urllib.request.urlopen(req, timeout=30, context=self._ssl_ctx) as resp:
            return json.loads(resp.read().decode())

    def submit_heatmap(self, params):
        """Submit heatmap request, return raw response."""
        return self._make_request("POST", "/heatmap", params)

    def submit_env_params(self, params):
        """Submit env_params request, return raw response."""
        return self._make_request("POST", "/env_params", params)

    def poll_status(self, activity_id, max_polls=30, interval=3):
        """Poll until terminal state."""
        for i in range(max_polls):
            time.sleep(interval)
            result = self._make_request("GET", f"/status/{activity_id}")
            status = result.get("data", {}).get("status", "unknown")
            if status in ("Completed", "Failed"):
                return result
        raise TimeoutError(f"Activity {activity_id} did not reach terminal status")
