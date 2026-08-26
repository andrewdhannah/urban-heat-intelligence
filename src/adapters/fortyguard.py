"""
FortyGuard Temperature API Adapter — Minimal S0 Runtime Slice

Provides authenticated access to FortyGuard's heatmap and env_params endpoints.
This is the minimum viable adapter for S0 preflight validation.

Evidence receipts are generated for every API call.
"""

import json
import hashlib
import time
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime, timezone

BASE_URL = "https://api.fortyguard.com/v1"

# Credential loading — never print, never serialize
def load_api_key():
    """Load FortyGuard API key from governed secret store."""
    env_path = Path(__file__).resolve().parent.parent.parent / ".secrets" / "fortyguard.env"
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line.startswith("FORTYGUARD_API_KEY="):
                return line.split("=", 1)[1]
    raise RuntimeError("FORTYGUARD_API_KEY not found in governed secret store")


def make_request(method, path, api_key, body=None):
    """Make authenticated request to FortyGuard API."""
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url, method=method)
    req.add_header("api-key", api_key)
    req.add_header("Content-Type", "application/json")
    if body:
        req.data = json.dumps(body).encode()
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def poll_status(activity_id, api_key, max_polls=30, interval=3):
    """Poll activity status until terminal state."""
    for i in range(max_polls):
        time.sleep(interval)
        result = make_request("GET", f"/status/{activity_id}", api_key)
        status = result.get("data", {}).get("status", "unknown")
        if status in ("Completed", "Failed"):
            return result
    raise TimeoutError(f"Activity {activity_id} did not reach terminal status")


def generate_receipt(provider, endpoint, request_params, activity_id,
                     terminal_status, response_timestamp, live_or_replay,
                     fixture_reference=None):
    """Generate evidence receipt for API call."""
    return {
        "receipt": {
            "provider": provider,
            "endpoint": endpoint,
            "request_parameters": request_params,
            "request_timestamp": datetime.now(timezone.utc).isoformat(),
            "activity_id": activity_id,
            "terminal_status": terminal_status,
            "response_timestamp": response_timestamp,
            "fixture_reference": fixture_reference,
            "authentication": "api-key",
            "credential_source": "FORTYGUARD_API_KEY",
            "credential_present": True,
            "credential_exposed": False,
            "live_or_replay": live_or_replay,
            "content_hash": "sha256:" + hashlib.sha256(
                json.dumps(request_params, sort_keys=True).encode()
            ).hexdigest()[:16]
        }
    }
