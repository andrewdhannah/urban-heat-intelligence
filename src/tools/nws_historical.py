"""
NWS Historical Observation — Station observation for Replay context.

Provides a deterministic historical NWS station observation at or nearest
the Aug 25 14:00 MST FortyGuard Replay time.

Governed retrieval contract:
  1. Query /stations/{stationId}/observations with start/end parameters
     around the target time (±10 minutes).
  2. Filter to valid observations (non-null temperature).
  3. Select the observation with minimum absolute temporal distance
     from the target.
  4. Exact timestamp match wins over offset observations.
  5. On equal non-zero distance, prefer at-or-before target.
  6. If no valid observations found, return not_proven.

Station: KPHX (Phoenix Sky Harbor)
  - Closest official NWS station to the FortyGuard downtown Phoenix AOI
  - Confirmed via NWS station endpoint

This is a historical NWS STATION OBSERVATION.
It is NOT a forecast-period data, NOT a FortyGuard thermal measurement.
The two measure different physical quantities and must not be presented
as equivalent.
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
        with urllib.request.urlopen(req, timeout=15, context=_ssl_ctx) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return None


def get_historical_observation():
    """
    Retrieve the KPHX station observation nearest to Aug 25 14:00 MST.

    Governed selection rule:
    1. Query with bounded start/end window (±10 min from target).
    2. Filter to valid observations (non-null temperature).
    3. Select minimum absolute temporal distance from 21:00 UTC.
    4. Exact timestamp match wins.
    5. On equal non-zero distance, prefer at-or-before target.
    6. If no valid observations found, return not_proven.
    """
    window_minutes = 10
    start_utc = TARGET_TIME_UTC - timedelta(minutes=window_minutes)
    end_utc = TARGET_TIME_UTC + timedelta(minutes=window_minutes)

    params = (
        f"?start={start_utc.strftime('%Y-%m-%dT%H:%M:%SZ')}"
        f"&end={end_utc.strftime('%Y-%m-%dT%H:%M:%SZ')}"
        f"&limit=20"
    )
    data = _nws_get(f"/stations/{PHOENIX_STATION}/observations{params}")
    if not data:
        return {
            "status": "retrieval_failed",
            "reason": "NWS API request failed",
            "station": PHOENIX_STATION,
            "query": {"start": start_utc.isoformat(), "end": end_utc.isoformat()}
        }

    features = data.get("features", [])
    if not features:
        return {
            "status": "not_proven",
            "reason": f"No observations in window {start_utc.isoformat()} to {end_utc.isoformat()}",
            "station": PHOENIX_STATION,
            "query": {"start": start_utc.isoformat(), "end": end_utc.isoformat()}
        }

    # Filter to valid observations
    candidates = []
    for f in features:
        props = f.get("properties", {})
        ts_str = props.get("timestamp")
        temp = props.get("temperature", {})
        if not ts_str or temp.get("value") is None:
            continue
        try:
            ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            continue
        offset = abs((ts - TARGET_TIME_UTC).total_seconds())
        candidates.append({
            "timestamp": ts_str,
            "offset_seconds": offset,
            "props": props
        })

    if not candidates:
        return {
            "status": "not_proven",
            "reason": "No valid observations with temperature in window",
            "station": PHOENIX_STATION,
            "query": {"start": start_utc.isoformat(), "end": end_utc.isoformat()},
            "raw_count": len(features)
        }

    # Selection: minimum absolute distance, exact wins, at-or-before tie
    best = min(candidates, key=lambda c: (
        c["offset_seconds"],
        0 if datetime.fromisoformat(c["timestamp"].replace("Z", "+00:00")) <= TARGET_TIME_UTC else 1
    ))

    props = best["props"]
    ts = datetime.fromisoformat(best["timestamp"].replace("Z", "+00:00"))
    temp = props.get("temperature", {})
    wind_speed = props.get("windSpeed", {})
    wind_dir = props.get("windDirection", {})
    humidity = props.get("relativeHumidity", {})
    pressure = props.get("barometricPressure", {})
    visibility = props.get("visibility", {})
    heat_index = props.get("heatIndex", {})
    dewpoint = props.get("dewpoint", {})

    return {
        "status": "resolved",
        "station": PHOENIX_STATION,
        "station_name": None,
        "text_description": props.get("textDescription", ""),
        "observation_timestamp": best["timestamp"],
        "target_time_utc": TARGET_TIME_UTC.isoformat(),
        "offset_minutes": round(best["offset_seconds"] / 60),
        "selection_rule": "minimum absolute distance from target; exact match wins; at-or-before tie",
        "temperature": temp,
        "dewpoint": dewpoint,
        "wind_speed": wind_speed,
        "wind_direction": wind_dir,
        "relative_humidity": humidity,
        "barometric_pressure": pressure,
        "visibility": visibility,
        "heat_index": heat_index,
        "raw_message": props.get("rawMessage", ""),
        "raw_window_count": len(features),
        "valid_candidate_count": len(candidates),
        "provenance": {
            "provider": "NWS",
            "endpoint": f"/stations/{PHOENIX_STATION}/observations",
            "query_params": {"start": start_utc.isoformat(), "end": end_utc.isoformat(), "limit": "20"},
            "station_identifier": PHOENIX_STATION,
            "data_type": "station_observation",
            "measurement_type": "air_temperature_at_station",
            "note": "NWS station air temperature is a point measurement. FortyGuard thermal-cell value is a measured surface/thermal value for a spatial cell. Different physical measurements.",
            "used_in_decision": False,
            "retrieved_at": datetime.now(timezone.utc).isoformat()
        }
    }
