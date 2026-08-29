"""
NWS Historical Observation — Station observation for Replay context.

Provides a deterministic historical NWS station observation at or nearest
the Aug 25 14:00 MST FortyGuard Replay time.

Deterministic rule:
  Station: KPHX (Phoenix Sky Harbor) — closest official NWS station to
  the FortyGuard downtown Phoenix AOI.
  Time: Aug 25, 2026, 14:00 MST (21:00 UTC) — the FortyGuard Replay
  observation time.
  Selection: Station observation with timestamp nearest to 21:00 UTC
  on Aug 25, 2026, preferring observations at or before the target time.

This is a FORECAST-PERIOD or STATION OBSERVATION from the NWS API.
It is NOT a FortyGuard thermal measurement. The two measure different
physical quantities and must not be presented as equivalent.
"""

import json
import ssl
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

NWS_BASE = "https://api.weather.gov"
PHOENIX_STATION = "KPHX"
HEADERS = {"User-Agent": "UrbanHeatIntelligence-Hackathon26"}
TARGET_TIME_UTC = datetime(2026, 8, 25, 21, 0, 0, tzinfo=timezone.utc)  # 14:00 MST

_ssl_ctx = ssl.create_default_context()
for ca_path in ["/etc/ssl/cert.pem", "/etc/ssl/certs/ca-certificates.crt"]:
    if Path(ca_path).exists():
        _ssl_ctx.load_verify_locations(ca_path)
        break


def _nws_get(path):
    url = f"{NWS_BASE}{path}"
    req = urllib.request.Request(url)
    for k, v in HEADERS.items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=10, context=_ssl_ctx) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return None


def get_historical_observation():
    """
    Retrieve the KPHX station observation nearest to Aug 25 14:00 MST.

    Deterministic selection rule:
    1. Fetch recent observations from /stations/KPHX/observations
    2. Filter to Aug 25, 2026 observations
    3. Select the observation with timestamp nearest to 21:00 UTC
       (preferring observations at or before the target time)
    4. If no Aug 25 observations available, return None (NOT PROVEN)
    """
    data = _nws_get(f"/stations/{PHOENIX_STATION}/observations?limit=24")
    if not data:
        return {"status": "unavailable", "reason": "NWS API request failed", "station": PHOENIX_STATION}

    features = data.get("features", [])
    if not features:
        return {"status": "unavailable", "reason": "No observations returned", "station": PHOENIX_STATION}

    # Filter to Aug 25, 2026 observations
    aug25_observations = []
    for f in features:
        props = f.get("properties", {})
        timestamp_str = props.get("timestamp")
        if not timestamp_str:
            continue
        try:
            ts = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            if ts.date() == TARGET_TIME_UTC.date():
                aug25_observations.append((ts, props))
        except (ValueError, TypeError):
            continue

    if not aug25_observations:
        return {"status": "not_proven", "reason": "No Aug 25 observations found in recent window", "station": PHOENIX_STATION}

    # Select nearest to target time, preferring at-or-before
    best = min(aug25_observations, key=lambda x: abs((x[0] - TARGET_TIME_UTC).total_seconds()))
    ts, props = best

    return {
        "status": "resolved",
        "station": PHOENIX_STATION,
        "station_name": props.get("textDescription", PHOENIX_STATION),
        "observation_timestamp": ts.isoformat(),
        "target_time_utc": TARGET_TIME_UTC.isoformat(),
        "offset_minutes": round((ts - TARGET_TIME_UTC).total_seconds() / 60),
        "temperature_celsius": props.get("temperature", {}).get("value"),
        "temperature_unit": "°C (raw from NWS)",
        "dewpoint_celsius": props.get("dewpoint", {}).get("value"),
        "wind_speed_ms": props.get("windSpeed", {}).get("value"),
        "wind_direction_deg": props.get("windDirection", {}).get("value"),
        "barometric_pressure_pa": props.get("barometricPressure", {}).get("value"),
        "relative_humidity": props.get("relativeHumidity", {}).get("value"),
        "heat_index_celsius": props.get("heatIndex", {}).get("value"),
        "wind_chill_celsius": props.get("windChill", {}).get("value"),
        "visibility_m": props.get("visibility", {}).get("value"),
        "precipitation_last_hour_mm": props.get("precipitationLastHour", {}).get("value"),
        "raw_message": props.get("rawMessage", ""),
        "provenance": {
            "provider": "NWS",
            "endpoint": f"/stations/{PHOENIX_STATION}/observations",
            "station_identifier": PHOENIX_STATION,
            "data_type": "station_observation",
            "measurement_type": "air_temperature_at_station",
            "note": "NWS station air temperature ≠ FortyGuard thermal-cell temperature",
            "used_in_decision": False,
            "retrieved_at": datetime.now(timezone.utc).isoformat()
        }
    }
