"""
Normalized Tool Contracts — FortyGuard Environmental Parameters

Provides a stable application-level interface around the raw FortyGuard API.
"""

import json
import hashlib
from datetime import datetime, timezone


def _derive_observation_time(request_params, provider_metadata=None):
    """Derive observation time from provider metadata or request date_time."""
    # Prefer provider metadata timestamps
    if provider_metadata:
        time_range = provider_metadata.get("time_range", {})
        start = time_range.get("start")
        if start:
            return start

    # Fall back to request date_time
    dt = request_params.get("date_time", {})
    start_date = dt.get("start_date", "")
    start_time = dt.get("start_time", "")
    if start_date and start_time:
        return f"{start_date}T{start_time}:00-07:00"
    elif start_date:
        return f"{start_date}T12:00:00-07:00"
    return None


def normalize_env_params_result(raw_response, request_params, mode="live", fixture_path=None, activity_id=None):
    """
    Normalize FortyGuard env_params response into stable application contract.

    Args:
        raw_response: Raw API response dict (data.result structure)
        request_params: Original request parameters
        mode: "live" or "replay"
        fixture_path: Path to fixture file if replay
        activity_id: Provider activity ID if available

    Returns:
        Normalized env_params result dict
    """
    result = raw_response.get("result", raw_response)
    metadata = result.get("metadata", {})
    locations = result.get("locations", [])

    # Extract first location's parameters
    loc = locations[0] if locations else {}
    params = loc.get("parameters", {})

    # Normalize key parameters
    heat_index = None
    apparent_temp = None
    humidity = None

    def _extract(val):
        if isinstance(val, list) and len(val) > 0:
            return val[0]
        return val

    if isinstance(params, dict):
        heat_index = _extract(params.get("heat_index_celsius"))
        apparent_temp = _extract(params.get("apparent_temperature_celsius"))
        humidity = _extract(params.get("relative_humidity_percent"))
    elif isinstance(params, list):
        for p in params:
            name = p.get("name", "")
            value = p.get("value")
            if name == "heat_index_celsius" and value is not None:
                heat_index = value
            elif name == "apparent_temperature_celsius" and value is not None:
                apparent_temp = value
            elif name == "relative_humidity_percent" and value is not None:
                humidity = value

    solar = loc.get("solar_irradiance")
    solar_irradiance = None
    if solar and isinstance(solar, dict):
        solar_irradiance = _extract(solar.get("value")) or solar.get("ghi")

    # Derive observation time from provider metadata (preferred) or request
    observation_time = _derive_observation_time(request_params, metadata)

    return {
        "tool": "get_environmental_parameters",
        "provider": "FortyGuard",
        "endpoint": "/v1/env_params",
        "mode": mode,
        "observation_time": observation_time,
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "activity_id": activity_id,
        "request": {
            "latitude": request_params.get("latitude"),
            "longitude": request_params.get("longitude"),
            "temperature": request_params.get("temperature"),
            "date_time": request_params.get("date_time")
        },
        "result": {
            "coordinate": {
                "latitude": request_params.get("latitude"),
                "longitude": request_params.get("longitude")
            },
            "temperature_celsius": request_params.get("temperature"),
            "heat_index_celsius": heat_index,
            "apparent_temperature_celsius": apparent_temp,
            "relative_humidity_percent": humidity,
            "solar_irradiance": solar_irradiance,
            "timezone": metadata.get("timezone"),
            "time_range": metadata.get("time_range"),
        },
        "all_parameters": [
            {"name": k, "value": v}
            for k, v in params.items()
        ] if isinstance(params, dict) else [
            {"name": p.get("name"), "value": p.get("value"), "unit": p.get("unit")}
            for p in params
        ],
        "fixture_reference": fixture_path,
        "content_hash": "sha256:" + hashlib.sha256(
            json.dumps(result, sort_keys=True).encode()
        ).hexdigest()[:16]
    }
