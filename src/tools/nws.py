"""
NWS Corroboration — Current conditions and active alerts for Phoenix.

Provides contextual weather data from the National Weather Service API.
Used as secondary corroboration alongside FortyGuard thermal observations.
"""

import json
import ssl
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path


NWS_BASE = "https://api.weather.gov"
PHOENIX_POINT = "33.45,-112.07"
HEADERS = {"User-Agent": "UrbanHeatIntelligence-Hackathon26"}


def _make_ssl_context():
    """Create verified SSL context with system CA bundle."""
    ctx = ssl.create_default_context()
    for ca_path in ["/etc/ssl/cert.pem", "/etc/ssl/certs/ca-certificates.crt"]:
        if Path(ca_path).exists():
            ctx.load_verify_locations(ca_path)
            break
    return ctx


_ssl_ctx = _make_ssl_context()


def _nws_get(path):
    """Make a request to the NWS API."""
    url = f"{NWS_BASE}{path}"
    req = urllib.request.Request(url)
    for k, v in HEADERS.items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=10, context=_ssl_ctx) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return None


def get_current_conditions():
    """Get current forecast conditions for Phoenix."""
    data = _nws_get(f"/gridpoints/PSR/128,48/forecast")
    if not data:
        return None
    periods = data.get("properties", {}).get("periods", [])
    if not periods:
        return None
    current = periods[0]
    return {
        "source": "NWS",
        "type": "current_conditions",
        "source_endpoint": "/gridpoints/PSR/128,48/forecast",
        "period_name": current.get("name"),
        "temperature_f": current.get("temperature"),
        "temperature_unit": current.get("temperatureUnit"),
        "short_forecast": current.get("shortForecast"),
        "detailed_forecast": current.get("detailedForecast", "")[:200],
        "wind_speed": current.get("windSpeed"),
        "wind_direction": current.get("windDirection"),
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "effective_start": current.get("startTime"),
        "effective_end": current.get("endTime")
    }


def get_active_alerts():
    """Get active weather alerts for the Phoenix area."""
    data = _nws_get(f"/alerts/active?point={PHOENIX_POINT}")
    if not data:
        return []
    features = data.get("features", [])
    alerts = []
    for f in features[:5]:  # Limit to 5 alerts
        props = f.get("properties", {})
        alerts.append({
            "source": "NWS",
            "type": "alert",
            "source_endpoint": "/alerts/active?point=33.45,-112.07",
            "event": props.get("event"),
            "headline": props.get("headline", "")[:150],
            "severity": props.get("severity"),
            "urgency": props.get("urgency"),
            "onset": props.get("onset"),
            "expires": props.get("expires"),
            "description": props.get("description", "")[:200]
        })
    return alerts


def get_nws_context():
    """Get combined NWS context for corroboration."""
    retrieved_at = datetime.now(timezone.utc).isoformat()
    conditions = get_current_conditions()
    alerts = get_active_alerts()
    return {
        "conditions": conditions,
        "alerts": alerts,
        "alert_count": len(alerts),
        "has_extreme_heat_warning": any(
            "heat" in (a.get("event", "").lower() + a.get("headline", "").lower())
            for a in alerts
        ),
        "provider": "NWS",
        "area": "Phoenix, AZ",
        "retrieved_at": retrieved_at,
        "source_endpoints": [
            "/gridpoints/PSR/128,48/forecast",
            "/alerts/active?point=33.45,-112.07"
        ]
    }
