"""
Normalized Tool Contracts — FortyGuard Heatmap

Provides a stable application-level interface around the raw FortyGuard API.
Agent calls this instead of reasoning over raw provider JSON.
"""

import json
import hashlib
from datetime import datetime, timezone


def _polygon_centroid(coords):
    """Calculate centroid of a polygon ring."""
    if not coords or len(coords) < 3:
        return coords[0] if coords else None
    # Simple average of vertices (good enough for small tiles)
    lngs = [c[0] for c in coords]
    lats = [c[1] for c in coords]
    return [round(sum(lngs) / len(lngs), 6), round(sum(lats) / len(lats), 6)]


def _derive_observation_time(request_params):
    """Derive observation time from request date_time params."""
    dt = request_params.get("date_time", {})
    start_date = dt.get("start_date", "")
    start_time = dt.get("start_time", "")
    if start_date and start_time:
        return f"{start_date}T{start_time}:00-07:00"  # Phoenix is GMT-7
    elif start_date:
        return f"{start_date}T12:00:00-07:00"
    return None


def normalize_heatmap_result(raw_response, request_params, mode="live", fixture_path=None, activity_id=None):
    """
    Normalize FortyGuard heatmap response into stable application contract.

    Args:
        raw_response: Raw API response dict (data.result structure)
        request_params: Original request parameters
        mode: "live" or "replay"
        fixture_path: Path to fixture file if replay
        activity_id: Provider activity ID if available

    Returns:
        Normalized heatmap result dict
    """
    result = raw_response.get("result", raw_response)
    map_data = result.get("map_data", {})
    stats_data = result.get("stats_data", {})

    features = map_data.get("features", [])

    # Extract temperatures from ALL features
    temps = []
    for f in features:
        props = f.get("properties", {})
        avg = props.get("average_temperature")
        if avg is not None:
            temps.append(avg)

    # Find GLOBAL hottest feature across ALL features
    hottest = None
    hottest_props = {}
    hottest_coord = None
    if features:
        hottest = max(features, key=lambda f: f.get("properties", {}).get("average_temperature", 0))
        hottest_props = hottest.get("properties", {})
        # Calculate centroid from polygon
        geom_coords = hottest.get("geometry", {}).get("coordinates", [[]])
        ring = geom_coords[0] if geom_coords else []
        hottest_coord = _polygon_centroid(ring)

    # Build candidates from ALL features, sorted by temperature
    candidates = []
    for f in features:
        props = f.get("properties", {})
        avg = props.get("average_temperature")
        if avg is None:
            continue
        geom_coords = f.get("geometry", {}).get("coordinates", [[]])
        ring = geom_coords[0] if geom_coords else []
        centroid = _polygon_centroid(ring)
        if centroid:
            candidates.append({
                "longitude": centroid[0],
                "latitude": centroid[1],
                "temperature_celsius": avg,
                "tile_id": props.get("tile_id")
            })
    candidates.sort(key=lambda c: c["temperature_celsius"], reverse=True)

    # Derive observation time from request (not current time)
    observation_time = _derive_observation_time(request_params)

    return {
        "tool": "get_heatmap",
        "provider": "FortyGuard",
        "endpoint": "/v1/heatmap",
        "mode": mode,
        "observation_time": observation_time,
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "activity_id": activity_id,
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
            "selection_method": "global_maximum_across_all_features_polygon_centroid",
            "tile_id": hottest_props.get("tile_id")
        },
        "candidates_for_env_params": candidates[:5],
        "fixture_reference": fixture_path,
        "content_hash": "sha256:" + hashlib.sha256(
            json.dumps(result, sort_keys=True).encode()
        ).hexdigest()[:16]
    }
