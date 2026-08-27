"""
Agent Controller — Heat-question answering with planning and evidence chain

8-node evidence chain (thermal):
    user_request → plan → heatmap_request → heatmap_result
    → coordinate_selection → env_params_request → env_params_result → answer

Context evidence chain (GIS):
    canopy_request → canopy_result → parks_request → parks_result
    → context_enrichment_result
"""

import json
from datetime import datetime, timezone

from src.tools.heatmap import normalize_heatmap_result
from src.tools.env_params import normalize_env_params_result
from src.tools.gis_context import enrich_candidate_context
from src.agent.time_resolver import resolve_latest_observation_time, resolve_latest_available_observation, format_observation_time

# Canonical near-tie threshold — single source of truth for ranking and Brief
TIE_THRESHOLD_CELSIUS = 0.1


def plan_question(question, context=None):
    """Minimal question planner — produces tool plan based on intent."""
    q = question.lower()

    # Decision/prioritization intent — highest priority
    if any(w in q for w in ["prioritize", "priority", "cooling intervention", "intervention", "where should"]):
        return {
            "interpreted_intent": "cooling_prioritization",
            "selected_tools": ["get_heatmap", "get_environmental_parameters"],
            "rationale": "Question asks for intervention prioritization; heatmap identifies hottest areas, env_params provides local conditions at priority location"
        }

    # Risk assessment intent
    if any(w in q for w in ["risk", "danger", "heat risk", "heat index", "how hot", "feel like"]):
        return {
            "interpreted_intent": "area_risk_assessment",
            "selected_tools": ["get_heatmap", "get_environmental_parameters"],
            "rationale": "Question asks about area-level heat risk; heatmap provides spatial distribution, env_params provides local conditions at representative location"
        }

    # Distribution intent — lowest priority, heatmap only
    if any(w in q for w in ["distribution", "spread", "across"]):
        return {
            "interpreted_intent": "temperature_distribution",
            "selected_tools": ["get_heatmap"],
            "rationale": "Question asks about spatial distribution; heatmap alone provides the needed temperature map across the area"
        }

    # Default: area risk
    return {
        "interpreted_intent": "area_risk_assessment",
        "selected_tools": ["get_heatmap", "get_environmental_parameters"],
        "rationale": "Default plan: heatmap for spatial context, env_params for local conditions"
    }


class HeatAgent:
    """Agent that answers heat questions using FortyGuard tools."""

    def __init__(self, adapter, mode="live"):
        self.adapter = adapter
        self.mode = mode
        self.evidence_chain = []
        self.context_evidence_chain = []

    def answer(self, question, location="Phoenix, AZ", date_time=None):
        """Answer a heat question with planning, tool calls, and 8-node evidence."""
        self.evidence_chain = []
        self.context_evidence_chain = []
        self.live_diagnostics = {}

        # Reset adapter request counters for this query
        if hasattr(self.adapter, 'reset_request_counts'):
            self.adapter.reset_request_counts()

        # For LIVE mode: use bounded lookback to find latest available observation
        # The discovery heatmap IS the answer heatmap - no duplicate execution
        heatmap_result = None
        if self.mode == "live" and date_time is None:
            lookback_result = resolve_latest_available_observation(self.adapter)
            self.live_diagnostics = lookback_result
            
            if lookback_result["found"]:
                # Reuse the heatmap result from discovery - no duplicate execution
                heatmap_result = lookback_result["heatmap_result"]
                date_time = lookback_result["observation_time"]
            else:
                # No data found in lookback window - return bounded error
                return self._error_answer(
                    "LIVE unavailable: No FortyGuard observation data found in the "
                    f"last {lookback_result['lookback_used']} hours. "
                    "Please try Replay mode for historical data."
                )

        # 1. user_request
        self._add_evidence("user_request", {
            "question": question,
            "location": location,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

        # 2. plan
        plan = plan_question(question)
        self._add_evidence("plan", {
            "interpreted_intent": plan["interpreted_intent"],
            "selected_tools": plan["selected_tools"],
            "rationale": plan["rationale"]
        })

        env_result = None

        if "get_heatmap" in plan["selected_tools"]:
            # 3. heatmap_request
            heatmap_request = self._build_heatmap_request(date_time)
            self._add_evidence("heatmap_request", {
                "endpoint": "/v1/heatmap",
                "mode": self.mode,
                "aoi": "Phoenix downtown (~0.02 degree polygon)",
                "requested_observation_time": format_observation_time(date_time) if date_time else None,
                "granularity": 100,
                "date_time": date_time
            })

            # 4. heatmap_result
            # For REPLAY: execute heatmap call
            # For LIVE: reuse result from lookback discovery (already set above)
            if heatmap_result is None:
                heatmap_result = self._call_heatmap(date_time)
            
            if heatmap_result is None:
                return self._error_answer("Heatmap call failed")

            self._add_evidence("heatmap_result", {
                "tool": "get_heatmap",
                "activity_id": heatmap_result.get("activity_id"),
                "feature_count": heatmap_result["result"]["feature_count"],
                "mean_temp": heatmap_result["result"]["mean_temperature_celsius"],
                "max_temp": heatmap_result["result"]["max_temperature_celsius"],
                "observation_time": heatmap_result["observation_time"],
                "mode": self.mode
            })

        if "get_environmental_parameters" in plan["selected_tools"] and heatmap_result:
            candidates = heatmap_result.get("candidates_for_env_params", [])
            if not candidates:
                return self._error_answer("No temperature candidates found")

            # Top-3 candidate comparison
            top_n = min(3, len(candidates))
            ranked_candidates = []

            for i in range(top_n):
                cand = candidates[i]
                # 5. coordinate_selection (for each candidate)
                self._add_evidence("coordinate_selection", {
                    "selected_coordinate": cand,
                    "selection_method": f"top_{i+1}_temperature_feature",
                    "rank": i + 1,
                    "observation_time": heatmap_result["observation_time"]
                })

                # 6. env_params_request
                self._add_evidence("env_params_request", {
                    "endpoint": "/v1/env_params",
                    "mode": self.mode,
                    "coordinate": {"latitude": cand["latitude"], "longitude": cand["longitude"]},
                    "temperature_supplied": cand["temperature_celsius"],
                    "requested_observation_time": format_observation_time(date_time) if date_time else None
                })

                # 7. env_params_result
                env_result = self._call_env_params(cand, date_time)
                if env_result is None:
                    continue  # Skip failed candidates

                self._add_evidence("env_params_result", {
                    "tool": "get_environmental_parameters",
                    "activity_id": env_result.get("activity_id"),
                    "heat_index": env_result["result"]["heat_index_celsius"],
                    "apparent_temp": env_result["result"]["apparent_temperature_celsius"],
                    "humidity": env_result["result"]["relative_humidity_percent"],
                    "observation_time": env_result["observation_time"],
                    "mode": self.mode,
                    "rank": i + 1
                })

                ranked_candidates.append({
                    "rank": i + 1,
                    "coordinate": [cand["longitude"], cand["latitude"]],
                    "observed_temp": cand["temperature_celsius"],
                    "tile_id": cand.get("tile_id"),
                    "heat_index": env_result["result"]["heat_index_celsius"],
                    "apparent_temp": env_result["result"]["apparent_temperature_celsius"],
                    "humidity": env_result["result"]["relative_humidity_percent"],
                    "observation_time": env_result["observation_time"],
                    "env_params_activity_id": env_result.get("activity_id"),
                    "selection_method": f"top_{i+1}_temperature_feature"
                })

            if not ranked_candidates:
                return self._error_answer("Environmental parameters call failed for all candidates")

        # 8. answer
        answer = self._compose_answer(heatmap_result, env_result, question, location, plan,
                                      ranked_candidates=ranked_candidates if "get_environmental_parameters" in plan["selected_tools"] else None)

        self._add_evidence("answer", {
            "summary": answer["answer"]["summary"],
            "mode": self.mode,
            "observation_time": answer["answer"]["observation_time"],
            "source_nodes": ["heatmap_result", "env_params_result"]
        })

        # 9. GIS context enrichment (composition, not modification of thermal chain)
        # GIS context is additive and contextual—MUST NOT alter ranking
        # GIS failure MUST NOT invalidate thermal result
        if ranked_candidates:
            # Enrich top-3 candidates with GIS context
            all_context_evidence = []
            candidate_contexts = {}
            
            for i, candidate in enumerate(ranked_candidates):
                lat = candidate["coordinate"][1]
                lon = candidate["coordinate"][0]
                
                try:
                    context_result = enrich_candidate_context(
                        latitude=lat,
                        longitude=lon,
                        mode=self.mode,
                        adapter=None  # Level A: no live GIS adapter yet
                    )
                    
                    # Store per-candidate context
                    candidate_contexts[i] = context_result["context"]
                    all_context_evidence.extend(context_result["context_evidence_chain"])
                except Exception:
                    # GIS failure must not kill thermal result
                    candidate_contexts[i] = {"available": False, "canopy": None, "parks": None}
            
            self.context_evidence_chain = all_context_evidence
            
            # Store top-candidate context at top level for brief composition
            answer["context"] = candidate_contexts.get(0, {"available": False})
            answer["candidate_contexts"] = candidate_contexts
            answer["context_evidence_chain"] = self.context_evidence_chain

        # Add provider metrics to answer for traffic accounting
        # These are actual HTTP request counts from the adapter
        if hasattr(self.adapter, 'get_request_counts'):
            answer["provider_metrics"] = self.adapter.get_request_counts()
        else:
            answer["provider_metrics"] = {}

        return answer

    def _build_heatmap_request(self, date_time):
        return {
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
            "date_time": date_time or {"start_date": "2026-08-25", "start_time": "14:00", "filter_type": 1},
            "granularity": 100
        }

    def _call_heatmap(self, date_time):
        if self.mode == "replay":
            return self._replay_heatmap()
        return self._live_heatmap(date_time)

    def _live_heatmap(self, date_time):
        request_params = self._build_heatmap_request(date_time)
        try:
            raw = self.adapter.submit_heatmap(request_params)
            activity_id = raw.get("data", {}).get("activity_id")
            if not activity_id:
                return None
            status_result = self.adapter.poll_status(activity_id)
            status_data = status_result.get("data", {})
            if status_data.get("status") != "Completed":
                return None
            result = normalize_heatmap_result(
                status_data, request_params, mode="live", activity_id=activity_id
            )
            # Store the actual observation time for diagnostic reporting
            if result and date_time:
                result["requested_observation_time"] = date_time
            return result
        except Exception:
            return None

    def _replay_heatmap(self):
        from pathlib import Path
        fixture_path = Path("fixtures/fortyguard/heatmap/phoenix-2026-08-25-14h.json")
        if not fixture_path.exists():
            return None
        if not self._validate_fixture_integrity(fixture_path, "heatmap"):
            return None
        with open(fixture_path) as f:
            raw = json.load(f)
        data = raw.get("data", {})
        request_params = {
            "date_time": {"start_date": "2026-08-25", "start_time": "14:00", "filter_type": 1},
            "granularity": 100
        }
        return normalize_heatmap_result(
            data, request_params, mode="replay",
            fixture_path=str(fixture_path),
            activity_id=data.get("activity_id")
        )

    def _call_env_params(self, coordinate, date_time):
        if self.mode == "replay":
            return self._replay_env_params()
        return self._live_env_params(coordinate, date_time)

    def _live_env_params(self, coordinate, date_time):
        request_params = {
            "latitude": coordinate["latitude"],
            "longitude": coordinate["longitude"],
            "temperature": coordinate["temperature_celsius"],
            "date_time": date_time or {"start_date": "2026-08-25", "start_time": "14:00", "filter_type": 1}
        }
        try:
            raw = self.adapter.submit_env_params(request_params)
            activity_id = raw.get("data", {}).get("activity_id")
            if not activity_id:
                return None
            status_result = self.adapter.poll_status(activity_id)
            status_data = status_result.get("data", {})
            if status_data.get("status") != "Completed":
                return None
            return normalize_env_params_result(
                status_data, request_params, mode="live", activity_id=activity_id
            )
        except Exception:
            return None

    def _replay_env_params(self):
        from pathlib import Path
        fixture_path = Path("fixtures/fortyguard/env_params/phoenix-33.4484--112.0740-2026-08-25-14h.json")
        if not fixture_path.exists():
            return None
        if not self._validate_fixture_integrity(fixture_path, "env_params"):
            return None
        with open(fixture_path) as f:
            raw = json.load(f)
        data = raw.get("data", {})
        request_params = {
            "latitude": 33.4484, "longitude": -112.0740,
            "temperature": 42.0,
            "date_time": {"start_date": "2026-08-25", "start_time": "14:00", "filter_type": 1}
        }
        return normalize_env_params_result(
            data, request_params, mode="replay",
            fixture_path=str(fixture_path),
            activity_id=data.get("activity_id")
        )

    @staticmethod
    def _validate_fixture_integrity(fixture_path, fixture_type):
        """Validate fixture against integrity manifest (SPEC-012)."""
        from pathlib import Path
        import hashlib
        manifest_path = Path("fixtures/fortyguard/integrity-manifest.json")
        if not manifest_path.exists():
            return True  # No manifest = skip validation (backward compatible)
        try:
            with open(manifest_path) as f:
                manifest = json.load(f)
            expected_hash = None
            for fx in manifest.get("fixtures", []):
                if fx.get("type") == fixture_type and fx.get("path") == str(fixture_path):
                    expected_hash = fx.get("sha256")
                    break
            if expected_hash is None:
                return True  # Fixture not in manifest = skip validation
            actual_hash = hashlib.sha256(fixture_path.read_bytes()).hexdigest()
            return actual_hash == expected_hash
        except Exception:
            return False  # Integrity check failure = do not use fixture

    def _compose_answer(self, heatmap, env_params, question, location, plan, ranked_candidates=None):
        hm = heatmap["result"] if heatmap else {}
        ep = env_params["result"] if env_params else {}

        apparent_delta = None
        if ep.get("apparent_temperature_celsius") and ep.get("temperature_celsius"):
            apparent_delta = round(ep["apparent_temperature_celsius"] - ep["temperature_celsius"], 1)

        obs_time = heatmap["observation_time"] if heatmap else (env_params["observation_time"] if env_params else None)

        sources = []
        if heatmap:
            sources.append({"provider": "FortyGuard", "endpoint": "/v1/heatmap", "mode": heatmap["mode"],
                            "observation_time": heatmap["observation_time"], "activity_id": heatmap.get("activity_id")})
        if env_params:
            sources.append({"provider": "FortyGuard", "endpoint": "/v1/env_params", "mode": env_params["mode"],
                            "observation_time": env_params["observation_time"], "activity_id": env_params.get("activity_id")})

        # Build summary based on whether observation is live or historical
        if self.mode == "live":
            summary = f"Latest available FortyGuard observation for {location}: area experiencing very high thermal conditions."
        else:
            summary = f"The queried area in {location} is experiencing very high thermal conditions."

        # Build ranked candidates with comparative analysis
        # Near-tie detection: if thermal differences are below threshold,
        # candidates are effectively tied on measured burden.
        ranking_status = "ranked"
        ranking_explanation = None

        candidates_for_response = []
        if ranked_candidates:
            area_mean = hm.get("mean_temperature_celsius", 0)
            temps = [c["observed_temp"] for c in ranked_candidates]
            max_spread = max(temps) - min(temps) if len(temps) > 1 else 0

            if max_spread < TIE_THRESHOLD_CELSIUS:
                ranking_status = "near_tie"
                ranking_explanation = (
                    f"These candidate locations are effectively tied on measured thermal burden "
                    f"(spread: {round(max_spread, 3)}°C, threshold: {TIE_THRESHOLD_CELSIUS}°C). "
                    f"Additional local context (GIS, land cover, population density) would be needed "
                    f"to distinguish intervention priority."
                )

            for cand in ranked_candidates:
                delta_from_mean = round(cand["observed_temp"] - area_mean, 2) if area_mean else None
                candidates_for_response.append({
                    "rank": cand["rank"],
                    "coordinate": cand["coordinate"],
                    "observed_temp": cand["observed_temp"],
                    "delta_from_area_mean": delta_from_mean,
                    "heat_index": cand["heat_index"],
                    "apparent_temp": cand["apparent_temp"],
                    "humidity": cand["humidity"],
                    "selection_method": cand["selection_method"],
                    "tile_id": cand.get("tile_id")
                })

        return {
            "answer": {
                "summary": summary,
                "conditions": {
                    "area_mean_temperature_celsius": hm.get("mean_temperature_celsius"),
                    "area_max_temperature_celsius": hm.get("max_temperature_celsius"),
                    "area_min_temperature_celsius": hm.get("min_temperature_celsius"),
                    "area_temperature_range_celsius": hm.get("temperature_range_celsius"),
                    "feature_count": hm.get("feature_count"),
                    "representative_location": {
                        "heat_index_celsius": ep.get("heat_index_celsius"),
                        "apparent_temperature_celsius": ep.get("apparent_temperature_celsius"),
                        "relative_humidity_percent": ep.get("relative_humidity_percent"),
                        "measured_temperature_celsius": ep.get("temperature_celsius"),
                    },
                    "measured_result": {
                        "apparent_vs_measured_delta_celsius": apparent_delta,
                        "interpretation": "Apparent temperature exceeds measured temperature due to solar and environmental factors"
                    },
                    "ranked_candidates": candidates_for_response,
                    "ranking_status": ranking_status,
                    "ranking_explanation": ranking_explanation,
                    "tie_threshold_celsius": TIE_THRESHOLD_CELSIUS
                },
                "why_this_answer": plan.get("rationale", ""),
                "sources": sources,
                "mode": self.mode,
                "observation_time": obs_time
            },
            "evidence_chain": self.evidence_chain,
            "raw_results": {"heatmap": heatmap, "env_params": env_params}
        }

    def _error_answer(self, message):
        # Include provider metrics even in error case
        if hasattr(self.adapter, 'get_request_counts'):
            metrics = self.adapter.get_request_counts()
        else:
            metrics = {}
        return {
            "answer": {"summary": f"Unable to answer: {message}", "conditions": {},
                       "why_this_answer": message, "sources": [], "mode": self.mode,
                       "observation_time": None, "error": True},
            "evidence_chain": self.evidence_chain,
            "raw_results": {},
            "provider_metrics": metrics
        }

    def _add_evidence(self, step, data):
        self.evidence_chain.append({
            "step": step, "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
