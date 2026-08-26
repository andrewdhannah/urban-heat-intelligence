"""
Normalized Tool Contracts — FortyGuard Heatmap

Provides a stable application-level interface around the raw FortyGuard API.
Agent calls this instead of reasoning over raw provider JSON.
"""

import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path

# Raw provider schema preserved for provenance
RAW_SCHEMA_REFERENCE = "fortyguard-v1-heatmap"


def normalize_heatmap_result(raw_response, request_params, mode="live", fixture_path=None):
    """
    Normalize FortyGuard heatmap response into stable application contract.

    Args:
        raw_response: Raw API response dict (data.result structure)
        request_params: Original request parameters
        mode: "live" or "replay"
        fixture_path: Path to fixture file if replay

    Returns:
        Normalized heatmap result dict
    """
    result = raw_response.get("result", raw_response)
    map_data = result.get("map_data", {})
    stats_data = result.get("stats_data", {})

    features = map_data.get("features", [])

    # Extract temperature statistics
    temps = []
    for f in features:
        props = f.get("properties", {})
        avg = props.get("average_temperature")
        if avg is not None:
            temps.append(avg)

    temp_stats = stats_data.get("temperature_stats", {})

    # Find hottest feature
    hottest = None
    if features:
        hottest = max(features, key=lambda f: f.get("properties", {}).get("average_temperature", 0))
        hottest_props = hottest.get("properties", {})
        hottest_geom = hottest.get("geometry", {}).get("coordinates", [[]])[0]
        # Get centroid approximation (first coordinate pair)
        hottest_coord = hottest_geom[0] if hottest_geom else None
    else:
        hottest_props = {}
        hottest_coord = None

    # Build coordinate candidates for env_params
    candidates = []
    for f in features[:5]:  # Top 5 by position
        props = f.get("properties", {})
        geom = f.get("geometry", {}).get("coordinates", [[]])[0]
        if geom and props.get("average_temperature"):
            candidates.append({
                "longitude": geom[0][0] if geom else None,
                "latitude": geom[0][1] if geom else None,
                "temperature_celsius": props.get("average_temperature")
            })

    # Sort candidates by temperature (hottest first)
    candidates.sort(key=lambda c: c.get("temperature_celsius", 0), reverse=True)

    return {
        "tool": "get_heatmap",
        "provider": "FortyGuard",
        "endpoint": "/v1/heatmap",
        "mode": mode,
        "observation_time": datetime.now(timezone.utc).isoformat(),
        "request": {
            "polygon_aoi": request_params.get("polygon_aoi"),
            "date_time": request_params.get("date_time"),
            "granularity": request_params.get("granularity")
        },
        "result": {
            "feature_count": len(features),
            "min_temperature_celsius": min(temps) if temps else None,
            "max_temperature_celsius": max(temps) if temps else None,
            "mean_temperature_celsius": round(sum(temps) / len(temps), 2) if temps else None,
            "temperature_range_celsius": round(max(temps) - min(temps), 2) if temps else None,
        },
        "hottest_feature": {
            "temperature_celsius": hottest_props.get("average_temperature"),
            "coordinate": hottest_coord,
            "tile_id": hottest_props.get("tile_id")
        },
        "candidates_for_env_params": candidates,
        "fixture_reference": fixture_path,
        "content_hash": "sha256:" + hashlib.sha256(
            json.dumps(result, sort_keys=True).encode()
        ).hexdigest()[:16]
    }
