"""
Time resolution for FortyGuard API requests.

Resolves the latest completed provider-supported observation hour
for a given timezone, with bounded lookback when the latest hour
has no usable data.
"""

from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo


# Maximum lookback hours for Live mode
MAX_LOOKBACK_HOURS = 12


def resolve_latest_observation_time(timezone_name="America/Phoenix"):
    """
    Resolve the latest completed FortyGuard-supported observation hour.

    Args:
        timezone_name: IANA timezone name

    Returns:
        dict with start_date, start_time, filter_type for FortyGuard API
    """
    tz = ZoneInfo(timezone_name)
    now_local = datetime.now(tz)

    # Floor to the most recent completed hour
    latest_completed = now_local.replace(minute=0, second=0, microsecond=0) - timedelta(hours=1)

    return {
        "start_date": latest_completed.strftime("%Y-%m-%d"),
        "start_time": latest_completed.strftime("%H:%M"),
        "filter_type": 1
    }


def resolve_latest_available_observation(adapter, timezone_name="America/Phoenix", max_lookback=MAX_LOOKBACK_HOURS):
    """
    Resolve the latest available FortyGuard observation with bounded lookback.

    This function executes the heatmap query as part of discovery and returns
    the full result. The successful discovery heatmap IS the heatmap used by
    the answer - no duplicate execution.

    Args:
        adapter: FortyGuardAdapter instance for making API calls
        timezone_name: IANA timezone name
        max_lookback: Maximum hours to look back (default 12)

    Returns:
        dict with:
            - found: Whether a valid observation was found
            - observation_time: The resolved observation time dict
            - observation_time_iso: ISO string of the actual observation time
            - lookback_used: Number of hours looked back (0 if latest worked)
            - heatmap_result: Full normalized heatmap result (if found)
            - heatmap_activity_id: The activity ID (if found)
            - heatmap_request_params: The request params used (if found)
            - provider_metrics: Dict with submission/poll counts
    """
    from src.tools.heatmap import normalize_heatmap_result

    tz = ZoneInfo(timezone_name)
    now_local = datetime.now(tz)

    provider_metrics = {
        "heatmap_submissions": 0,
        "status_requests": 0
    }

    for lookback in range(max_lookback):
        # Calculate target hour
        target_time = now_local.replace(minute=0, second=0, microsecond=0) - timedelta(hours=lookback + 1)

        observation_time = {
            "start_date": target_time.strftime("%Y-%m-%d"),
            "start_time": target_time.strftime("%H:%M"),
            "filter_type": 1
        }

        # Build heatmap request (same as controller will use)
        request_params = {
            "polygon_aoi": {
                "type": "FeatureCollection",
                "features": [{
                    "type": "Feature",
                    "properties": {},
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[
                            [-112.08, 33.44], [-112.06, 33.44],
                            [-112.06, 33.46], [-112.08, 33.46],
                            [-112.08, 33.44]
                        ]]
                    }
                }]
            },
            "date_time": observation_time,
            "granularity": 100
        }

        try:
            # Submit heatmap request
            raw = adapter.submit_heatmap(request_params)
            provider_metrics["heatmap_submissions"] += 1

            activity_id = raw.get("data", {}).get("activity_id")
            if not activity_id:
                continue

            # Poll for completion (with bounded polling)
            status_result = adapter.poll_status(activity_id, max_polls=15, interval=3)
            provider_metrics["status_requests"] += 1

            status_data = status_result.get("data", {})
            if status_data.get("status") != "Completed":
                continue

            # Check for usable features
            result_data = status_data.get("result", {})
            map_data = result_data.get("map_data", {})
            features = map_data.get("features", [])

            if features:
                # Found usable data - normalize and return
                # This heatmap result IS the one used by the answer
                heatmap_result = normalize_heatmap_result(
                    status_data, request_params, mode="live", activity_id=activity_id
                )
                obs_time_iso = f"{observation_time['start_date']}T{observation_time['start_time']}:00-07:00"

                return {
                    "found": True,
                    "observation_time": observation_time,
                    "observation_time_iso": obs_time_iso,
                    "lookback_used": lookback,
                    "heatmap_result": heatmap_result,
                    "heatmap_activity_id": activity_id,
                    "heatmap_request_params": request_params,
                    "provider_metrics": provider_metrics
                }

        except Exception:
            # Skip this hour and continue lookback
            continue

    # No usable data found in lookback window
    return {
        "found": False,
        "observation_time": None,
        "observation_time_iso": None,
        "lookback_used": max_lookback,
        "heatmap_result": None,
        "heatmap_activity_id": None,
        "heatmap_request_params": None,
        "provider_metrics": provider_metrics
    }


def format_observation_time(api_date_time):
    """Format API date_time dict into human-readable ISO string."""
    if api_date_time is None:
        return None
    tz_offset = "-07:00"  # Phoenix is always GMT-7 (no DST)
    return f"{api_date_time['start_date']}T{api_date_time['start_time']}:00{tz_offset}"
