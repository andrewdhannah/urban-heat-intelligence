"""
Normalized Tool Contracts — FortyGuard Environmental Parameters

Provides a stable application-level interface around the raw FortyGuard API.
"""

import json
import hashlib
from datetime import datetime, timezone


def normalize_env_params_result(raw_response, request_params, mode="live", fixture_path=None):
    """
    Normalize FortyGuard env_params response into stable application contract.

    Args:
        raw_response: Raw API response dict (data.result structure)
        request_params: Original request parameters
        mode: "live" or "replay"
        fixture_path: Path to fixture file if replay

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
    solar_irradiance = None

    if isinstance(params, dict):
        # Dict format: {"heat_index_celsius": 39.3, ...} — value may be scalar or list
        def _extract(val):
            if isinstance(val, list) and len(val) > 0:
                return val[0]
            return val
        heat_index = _extract(params.get("heat_index_celsius"))
        apparent_temp = _extract(params.get("apparent_temperature_celsius"))
        humidity = _extract(params.get("relative_humidity_percent"))
    elif isinstance(params, list):
        # List format: [{"name": "heat_index_celsius", "value": 39.3}, ...]
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
    if solar and isinstance(solar, dict):
        solar_irradiance = solar.get("value") or solar.get("ghi")

    return {
        "tool": "get_environmental_parameters",
        "provider": "FortyGuard",
        "endpoint": "/v1/env_params",
        "mode": mode,
        "observation_time": datetime.now(timezone.utc).isoformat(),
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
