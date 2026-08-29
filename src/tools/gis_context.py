"""
Phoenix GIS Context Module — Tree Canopy and Parks enrichment.

Provides contextual information for FortyGuard thermal candidates using
authoritative City of Phoenix / MAG datasets. This module is additive and
contextual—GIS context MUST NOT become part of the thermal ranking.

Sources:
    - Tree Canopy: Phoenix Urban Heat Island and Tree Canopy Equity Analysis
      (City of Phoenix / Maricopa Association of Governments)
      Endpoint: https://services6.arcgis.com/SDdpEAs6WyhEBmTu/arcgis/rest/services/Phoenix_Urban_Heat_Island_and_Tree_Canopy_Equity_Analysis/FeatureServer/0
    - Parks: City of Phoenix mapped park data
      Endpoint: https://maps.phoenix.gov/pub/rest/services/Public/ParksOpenData/MapServer/10

Level A semantic constraints:
    - used_in_decision = false for all GIS claims
    - No parcel-level canopy implications
    - No current measurement claims
    - No distance claims without explicit calculation
    - No land-surface temperature as competing thermal measurement
"""

import json
import ssl
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List


# Canonical GIS provider identifiers
CANOPY_PROVIDER = "City of Phoenix / Maricopa Association of Governments"
CANOPY_DATASET = "Phoenix Urban Heat Island and Tree Canopy Equity Analysis"
CANOPY_REFERENCE_PERIOD = "2021"
CANOPY_ENDPOINT = "https://services6.arcgis.com/SDdpEAs6WyhEBmTu/arcgis/rest/services/Phoenix_Urban_Heat_Island_and_Tree_Canopy_Equity_Analysis/FeatureServer/0/query"

PARKS_PROVIDER = "City of Phoenix"
PARKS_DATASET = "City of Phoenix Mapped Parks"
PARKS_ENDPOINT = "https://maps.phoenix.gov/pub/rest/services/Public/ParksOpenData/MapServer/10/query"

INTERSECTION_PROVIDER = "City of Phoenix"
INTERSECTION_DATASET = "City of Phoenix Street Intersections"
INTERSECTION_ENDPOINT = "https://services6.arcgis.com/SDdpEAs6WyhEBmTu/arcgis/rest/services/Phoenix_Street_Intersections/FeatureServer/0/query"


def _now_iso() -> str:
    """Return current UTC time in ISO format."""
    return datetime.now(timezone.utc).isoformat()


def _get_ssl_context() -> ssl.SSLContext:
    """Create SSL context for GIS service queries."""
    ctx = ssl.create_default_context()
    return ctx


def _load_gis_fixture(fixture_name: str, mode: str) -> Optional[Dict[str, Any]]:
    """
    Load a GIS fixture file for replay mode.
    
    Args:
        fixture_name: Name of the fixture file (e.g., 'canopy.json')
        mode: 'live' or 'replay'
    
    Returns:
        Fixture data if found, None otherwise
    """
    if mode != "replay":
        return None
    
    fixture_path = Path(f"fixtures/phoenix-gis/{fixture_name}")
    if not fixture_path.exists():
        return None
    
    try:
        with open(fixture_path) as f:
            return json.load(f)
    except Exception:
        return None


def _validate_fixture_integrity(fixture_path: Path, fixture_type: str) -> bool:
    """
    Validate fixture against GIS integrity manifest.
    
    Args:
        fixture_path: Path to the fixture file
        fixture_type: Type of fixture ('canopy' or 'parks')
    
    Returns:
        True if integrity check passes, False otherwise
    
    Level A invariant: Replay GIS integrity is fail-closed.
    Missing manifest or unregistered fixture = integrity failure.
    """
    manifest_path = Path("fixtures/phoenix-gis/integrity-manifest.json")
    if not manifest_path.exists():
        return False  # Fail-closed: no manifest = integrity failure
    
    try:
        import hashlib
        with open(manifest_path) as f:
            manifest = json.load(f)
        
        expected_hash = None
        for fx in manifest.get("fixtures", []):
            if fx.get("type") == fixture_type and fx.get("path") == str(fixture_path):
                expected_hash = fx.get("sha256")
                break
        
        if expected_hash is None:
            return False  # Fail-closed: fixture not in manifest = integrity failure
        
        actual_hash = hashlib.sha256(fixture_path.read_bytes()).hexdigest()
        return actual_hash == expected_hash
    except Exception:
        return False  # Integrity check failure = do not use fixture


def _point_in_polygon(lat: float, lon: float, polygon_coords: List[List[float]]) -> bool:
    """
    Simple point-in-polygon test using ray casting algorithm.
    
    Args:
        lat: Latitude of test point
        lon: Longitude of test point
        polygon_coords: List of [longitude, latitude] coordinate pairs
    
    Returns:
        True if point is inside polygon
    """
    n = len(polygon_coords)
    inside = False
    
    j = n - 1
    for i in range(n):
        xi, yi = polygon_coords[i]
        xj, yj = polygon_coords[j]
        
        if ((yi > lat) != (yj > lat)) and (lon < (xj - xi) * (lat - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    
    return inside


def _query_arcgis_point(url: str, lon: float, lat: float, out_fields: str = "*") -> Dict[str, Any]:
    """
    Query an ArcGIS service with a point geometry.
    
    Args:
        url: ArcGIS query endpoint
        lon: Longitude
        lat: Latitude
        out_fields: Comma-separated field names
    
    Returns:
        Dict with:
            - success: bool indicating if query completed without error
            - features: list of feature attributes (empty if no features or on error)
            - error: error message if query failed, None otherwise
    
    This distinguishes between:
        1. Successful query with zero features (success=True, features=[])
        2. Query failure (success=False, features=[], error="...")
    """
    params = f"?geometry={lon},{lat}&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields={out_fields}&returnGeometry=false&f=json"
    ctx = _get_ssl_context()
    try:
        req = urllib.request.urlopen(url + params, timeout=15, context=ctx)
        data = json.loads(req.read())
        features = [f['attributes'] for f in data.get('features', [])]
        return {"success": True, "features": features, "error": None}
    except Exception as e:
        return {"success": False, "features": [], "error": str(e)}


def query_tree_canopy(
    latitude: float,
    longitude: float,
    mode: str = "live",
    adapter=None
) -> Dict[str, Any]:
    """
    Query tree canopy context for a candidate location.
    
    Args:
        latitude: Candidate latitude
        longitude: Candidate longitude
        mode: 'live' or 'replay'
        adapter: Optional GIS adapter for live queries (unused, kept for API compatibility)
    
    Returns:
        Dictionary with canopy context and provenance
    """
    evidence_node = {
        "step": "canopy_request",
        "data": {
            "provider": CANOPY_PROVIDER,
            "dataset": CANOPY_DATASET,
            "query_method": "server_side_point_in_polygon",
            "coordinate": {"latitude": latitude, "longitude": longitude},
            "mode": mode,
            "timestamp": _now_iso()
        }
    }
    
    if mode == "replay":
        fixture = _load_gis_fixture("canopy.json", mode)
        if fixture is None:
            return {
                "available": False,
                "error": "fixture_not_found",
                "evidence_node": evidence_node
            }
        
        fixture_path = Path("fixtures/phoenix-gis/canopy.json")
        if not _validate_fixture_integrity(fixture_path, "canopy"):
            return {
                "available": False,
                "error": "integrity_check_failed",
                "evidence_node": evidence_node
            }
        
        # Find the census tract containing this point
        for tract in fixture.get("census_tracts", []):
            polygon = tract.get("geometry", {}).get("coordinates", [[]])[0]
            if polygon and _point_in_polygon(latitude, longitude, polygon):
                result = {
                    "available": True,
                    "census_tract_geoid": tract["properties"]["geoid"],
                    "tree_canopy_pct": tract["properties"]["tree_canopy_pct"],
                    "source_provider": CANOPY_PROVIDER,
                    "dataset": CANOPY_DATASET,
                    "reference_period": CANOPY_REFERENCE_PERIOD,
                    "query_method": "server_side_point_in_polygon",
                    "retrieved_at": _now_iso(),
                    "used_in_decision": False,
                    "mode": mode
                }
                return {
                    "result": result,
                    "evidence_node": evidence_node,
                    "result_evidence_node": {
                        "step": "canopy_result",
                        "data": {
                            "provider": CANOPY_PROVIDER,
                            "dataset": CANOPY_DATASET,
                            "census_tract_geoid": result["census_tract_geoid"],
                            "tree_canopy_pct": result["tree_canopy_pct"],
                            "reference_period": CANOPY_REFERENCE_PERIOD,
                            "mode": mode,
                            "timestamp": _now_iso()
                        }
                    }
                }
        
        # Point not in any tract
        return {
            "available": False,
            "error": "point_not_in_census_tract",
            "evidence_node": evidence_node
        }
    
    # Live mode - query actual ArcGIS service
    query_result = _query_arcgis_point(
        CANOPY_ENDPOINT,
        longitude,
        latitude,
        "GEOID,mean_tree_canopy_pct"
    )
    
    if not query_result["success"]:
        # Query failed - GIS failure must not kill thermal result
        return {
            "available": False,
            "error": f"arcgis_query_failed: {query_result['error']}",
            "evidence_node": evidence_node
        }
    
    features = query_result["features"]
    if features:
        attrs = features[0]
        result = {
            "available": True,
            "census_tract_geoid": attrs.get("GEOID"),
            "tree_canopy_pct": attrs.get("mean_tree_canopy_pct"),
            "source_provider": CANOPY_PROVIDER,
            "dataset": CANOPY_DATASET,
            "reference_period": CANOPY_REFERENCE_PERIOD,
            "query_method": "server_side_point_in_polygon",
            "retrieved_at": _now_iso(),
            "used_in_decision": False,
            "mode": mode
        }
        return {
            "result": result,
            "evidence_node": evidence_node,
            "result_evidence_node": {
                "step": "canopy_result",
                "data": {
                    "provider": CANOPY_PROVIDER,
                    "dataset": CANOPY_DATASET,
                    "census_tract_geoid": result["census_tract_geoid"],
                    "tree_canopy_pct": result["tree_canopy_pct"],
                    "reference_period": CANOPY_REFERENCE_PERIOD,
                    "mode": mode,
                    "timestamp": _now_iso()
                }
            }
        }
    
    return {
        "available": False,
        "error": "no_features_returned",
        "evidence_node": evidence_node
    }


def query_parks(
    latitude: float,
    longitude: float,
    mode: str = "live",
    adapter=None,
    search_radius_meters: float = 1000.0
) -> Dict[str, Any]:
    """
    Query parks context for a candidate location.
    
    Args:
        latitude: Candidate latitude
        longitude: Candidate longitude
        mode: 'live' or 'replay'
        adapter: Optional GIS adapter for live queries (unused, kept for API compatibility)
        search_radius_meters: Radius for nearby park search (Level A: conservative claims only)
    
    Returns:
        Dictionary with parks context and provenance
    """
    evidence_node = {
        "step": "parks_request",
        "data": {
            "provider": PARKS_PROVIDER,
            "dataset": PARKS_DATASET,
            "query_method": "server_side_point_in_polygon",
            "coordinate": {"latitude": latitude, "longitude": longitude},
            "search_radius_meters": search_radius_meters,
            "mode": mode,
            "timestamp": _now_iso()
        }
    }
    
    if mode == "replay":
        fixture = _load_gis_fixture("parks.json", mode)
        if fixture is None:
            return {
                "available": False,
                "error": "fixture_not_found",
                "evidence_node": evidence_node
            }
        
        fixture_path = Path("fixtures/phoenix-gis/parks.json")
        if not _validate_fixture_integrity(fixture_path, "parks"):
            return {
                "available": False,
                "error": "integrity_check_failed",
                "evidence_node": evidence_node
            }
        
        inside_park = None
        coordinate_found = False
        
        # Look up authoritative per-candidate query results
        for candidate in fixture.get("candidate_results", []):
            coord = candidate.get("coordinate", {})
            # Match within ~10m tolerance (0.0001 degrees)
            if abs(coord.get("lat", 0) - latitude) < 0.0001 and abs(coord.get("lon", 0) - longitude) < 0.0001:
                coordinate_found = True
                features = candidate.get("provider_response", {}).get("features", [])
                if features:
                    attrs = features[0].get("attributes", {})
                    inside_park = {
                        "park_name": attrs.get("PROPERTY_NAME"),
                        "park_type": attrs.get("PARK_TYPE"),
                        "park_acres": attrs.get("PARK_ACRES")
                    }
                break
        
        # If coordinate not found in fixture, report unavailable
        if not coordinate_found:
            return {
                "available": False,
                "error": "candidate_not_in_fixture",
                "evidence_node": evidence_node
            }
        
        result = {
            "available": True,
            "inside_park": inside_park,
            "source_provider": PARKS_PROVIDER,
            "dataset": PARKS_DATASET,
            "retrieved_at": _now_iso(),
            "used_in_decision": False,
            "mode": mode
        }
        
        return {
            "result": result,
            "evidence_node": evidence_node,
            "result_evidence_node": {
                "step": "parks_result",
                "data": {
                    "provider": PARKS_PROVIDER,
                    "dataset": PARKS_DATASET,
                    "inside_park": inside_park is not None,
                    "park_name": inside_park["park_name"] if inside_park else None,
                    "mode": mode,
                    "timestamp": _now_iso()
                }
            }
        }
    
    # Live mode - query actual ArcGIS service
    query_result = _query_arcgis_point(
        PARKS_ENDPOINT,
        longitude,
        latitude,
        "PROPERTY_NAME,PARK_TYPE,PARK_ACRES"
    )
    
    if not query_result["success"]:
        # Query failed - GIS failure must not kill thermal result
        return {
            "available": False,
            "error": f"arcgis_query_failed: {query_result['error']}",
            "evidence_node": evidence_node
        }
    
    features = query_result["features"]
    inside_park = None
    nearby_parks = []
    
    if features:
        attrs = features[0]
        inside_park = {
            "park_name": attrs.get("PROPERTY_NAME"),
            "park_type": attrs.get("PARK_TYPE"),
            "park_acres": attrs.get("PARK_ACRES")
        }
    
    result = {
        "available": True,
        "inside_park": inside_park,
        "nearby_parks": nearby_parks,
        "source_provider": PARKS_PROVIDER,
        "dataset": PARKS_DATASET,
        "search_radius_meters": search_radius_meters,
        "retrieved_at": _now_iso(),
        "used_in_decision": False,
        "mode": mode
    }
    
    return {
        "result": result,
        "evidence_node": evidence_node,
        "result_evidence_node": {
            "step": "parks_result",
            "data": {
                "provider": PARKS_PROVIDER,
                "dataset": PARKS_DATASET,
                "inside_park": inside_park is not None,
                "park_name": inside_park["park_name"] if inside_park else None,
                "nearby_parks_count": len(nearby_parks),
                "mode": mode,
                "timestamp": _now_iso()
            }
        }
    }


def query_nearest_intersection(
    latitude: float,
    longitude: float,
    mode: str = "live"
) -> Dict[str, Any]:
    """
    Query nearest City of Phoenix street intersection for a candidate location.

    This is LOCAL CONTEXT only — used_in_decision=false.  Failure degrades
    gracefully to an unavailable result; it must not affect thermal ranking.

    Args:
        latitude: Candidate latitude
        longitude: Candidate longitude
        mode: 'live' or 'replay' (only executed for 'live')

    Returns:
        Dict with intersection name, distance in metres, and provenance.
    """
    evidence_node = {
        "step": "intersection_request",
        "data": {
            "provider": INTERSECTION_PROVIDER,
            "dataset": INTERSECTION_DATASET,
            "query_method": "nearest_feature",
            "coordinate": {"latitude": latitude, "longitude": longitude},
            "mode": mode,
            "timestamp": _now_iso()
        }
    }

    if mode != "live":
        return {
            "available": False,
            "error": "intersection_not_queried_in_replay",
            "evidence_node": evidence_node
        }

    # Query ArcGIS nearest feature — return nearest intersection with distance
    params = (
        f"?geometry={longitude},{latitude}"
        "&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects"
        "&outFields=FULL_NAME,PRE_DIR,STREET,STREETTYPE,SUF_DIR&returnGeometry=true"
        "&returnDistance=true&distance=200&units=esriSRUnit_Meter&f=json"
    )
    ctx = _get_ssl_context()
    try:
        req = urllib.request.urlopen(INTERSECTION_ENDPOINT + params, timeout=15, context=ctx)
        data = json.loads(req.read())
        features = data.get("features", [])
        if not features:
            return {
                "available": False,
                "error": "no_intersections_within_range",
                "evidence_node": evidence_node
            }
        # Find nearest by geometry distance attribute
        best = None
        best_dist = float("inf")
        for feat in features:
            attrs = feat.get("attributes", {})
            dist = attrs.get("dist", attrs.get("distance", float("inf")))
            if dist is not None and dist < best_dist:
                best_dist = dist
                best = attrs
        if best is None:
            return {
                "available": False,
                "error": "no_distance_attribute",
                "evidence_node": evidence_node
            }
        # Compose intersection name from attributes
        parts = [best.get("PRE_DIR", ""), best.get("STREET", ""), best.get("STREETTYPE", "")]
        name = " & ".join(filter(None, [best.get("FULL_NAME", ""), ""])).strip(" &")
        if not name:
            name = " ".join(filter(None, parts)).strip()
        result = {
            "available": True,
            "name": name or "Unknown intersection",
            "distance_m": round(best_dist, 0) if best_dist != float("inf") else None,
            "source_provider": INTERSECTION_PROVIDER,
            "dataset": INTERSECTION_DATASET,
            "used_in_decision": False,
            "mode": mode,
            "retrieved_at": _now_iso()
        }
        return {
            "result": result,
            "evidence_node": evidence_node,
            "result_evidence_node": {
                "step": "intersection_result",
                "data": {
                    "provider": INTERSECTION_PROVIDER,
                    "name": result["name"],
                    "distance_m": result["distance_m"],
                    "mode": mode,
                    "used_in_decision": False,
                    "timestamp": _now_iso()
                }
            }
        }
    except Exception as e:
        return {
            "available": False,
            "error": f"intersection_query_failed: {e}",
            "evidence_node": evidence_node
        }


def enrich_candidate_context(
    latitude: float,
    longitude: float,
    mode: str = "live",
    adapter=None,
    search_radius_meters: float = 1000.0
) -> Dict[str, Any]:
    """
    Enrich a candidate with Phoenix GIS context (canopy + parks).
    
    This is the main entry point for GIS context enrichment.
    GIS failure MUST NOT alter ranking, substitute fake context,
    convert Replay into Live, or suppress valid FortyGuard results.
    
    Args:
        latitude: Candidate latitude
        longitude: Candidate longitude
        mode: 'live' or 'replay'
        adapter: Optional GIS adapter for live queries
        search_radius_meters: Radius for nearby park search
    
    Returns:
        Dictionary with enriched context and evidence chain
    """
    context_evidence_chain = []
    
    # Query canopy
    canopy = query_tree_canopy(latitude, longitude, mode, adapter)
    if canopy.get("evidence_node"):
        context_evidence_chain.append(canopy["evidence_node"])
    if canopy.get("result_evidence_node"):
        context_evidence_chain.append(canopy["result_evidence_node"])
    
    # Query parks
    parks = query_parks(latitude, longitude, mode, adapter, search_radius_meters)
    if parks.get("evidence_node"):
        context_evidence_chain.append(parks["evidence_node"])
    if parks.get("result_evidence_node"):
        context_evidence_chain.append(parks["result_evidence_node"])

    # Query nearest intersection (LIVE only, local context)
    intersection = query_nearest_intersection(latitude, longitude, mode)
    if intersection.get("evidence_node"):
        context_evidence_chain.append(intersection["evidence_node"])
    if intersection.get("result_evidence_node"):
        context_evidence_chain.append(intersection["result_evidence_node"])

    # Build context result
    canopy_result = canopy.get("result")
    parks_result = parks.get("result")
    intersection_result = intersection.get("result")
    canopy_available = canopy_result.get("available", False) if isinstance(canopy_result, dict) else False
    parks_available = parks_result.get("available", False) if isinstance(parks_result, dict) else False
    intersection_available = intersection_result.get("available", False) if isinstance(intersection_result, dict) else False

    context = {
        "canopy": canopy_result if canopy_available else None,
        "parks": parks_result if parks_available else None,
        "intersection": intersection_result if intersection_available else None,
        "available": canopy_available or parks_available or intersection_available,
        "used_in_decision": False,
        "mode": mode,
        "retrieved_at": _now_iso()
    }
    
    # Add context enrichment result evidence
    context_evidence_chain.append({
        "step": "context_enrichment_result",
        "data": {
            "canopy_available": canopy_available,
            "parks_available": parks_available,
            "intersection_available": intersection_available,
            "context_available": context["available"],
            "mode": mode,
            "timestamp": _now_iso()
        }
    })
    
    return {
        "context": context,
        "context_evidence_chain": context_evidence_chain
    }


def format_canopy_claim(canopy: Optional[Dict[str, Any]]) -> Optional[str]:
    """
    Format canopy context for user-facing claim.
    
    Level A semantic constraints:
    - Must make granularity explicit (census tract level)
    - Must not imply parcel-level or current measurement
    - Must not claim causal relationship to temperature
    """
    if not canopy or not canopy.get("available"):
        return None
    
    tract_geoid = canopy.get("census_tract_geoid", "unknown")
    canopy_pct = canopy.get("tree_canopy_pct", 0)
    provider = canopy.get("source_provider", CANOPY_PROVIDER)
    reference = canopy.get("reference_period", CANOPY_REFERENCE_PERIOD)
    
    return (
        f"The candidate lies within census tract {tract_geoid} with {canopy_pct:.1f}% "
        f"tree canopy in the {provider} dataset ({reference})."
    )


def format_parks_claim(parks: Optional[Dict[str, Any]]) -> Optional[str]:
    """
    Format parks context for user-facing claim.
    
    Level A semantic constraints:
    - Do NOT claim distance without explicit calculation
    - Use conservative language: "inside" only
    """
    if not parks or not parks.get("available"):
        return None
    
    inside = parks.get("inside_park")
    
    if inside:
        return f"This candidate lies inside {inside['park_name']}."
    
    return "No mapped park at candidate location."
