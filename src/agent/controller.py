"""
Agent Controller — Heat-question answering agent with planning

Decides which tools to call based on user's heat question.
Composes evidence chain and produces structured answer.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

from src.tools.heatmap import normalize_heatmap_result
from src.tools.env_params import normalize_env_params_result


def plan_question(question, context=None):
    """
    Minimal question planner — produces tool plan based on intent.

    Returns:
        dict with interpreted_intent, selected_tools, rationale
    """
    q = question.lower()

    # Area risk question — needs heatmap + env_params
    if any(w in q for w in ["risk", "danger", "heat risk", "heat index", "how hot", "feel like"]):
        return {
            "interpreted_intent": "area_risk_assessment",
            "selected_tools": ["get_heatmap", "get_environmental_parameters"],
            "rationale": "Question asks about area-level heat risk; heatmap provides spatial distribution, env_params provides local conditions at representative location"
        }

    # Distribution question — needs heatmap only
    if any(w in q for w in ["distribution", "spread", "across", "map", "where"]):
        return {
            "interpreted_intent": "temperature_distribution",
            "selected_tools": ["get_heatmap"],
            "rationale": "Question asks about spatial distribution; heatmap alone provides the needed temperature map across the area"
        }

    # Default: area risk (most common)
    return {
        "interpreted_intent": "area_risk_assessment",
        "selected_tools": ["get_heatmap", "get_environmental_parameters"],
        "rationale": "Default plan: heatmap for spatial context, env_params for local conditions"
    }


class HeatAgent:
    """
    Agent that answers heat questions using FortyGuard tools.
    """

    def __init__(self, adapter, mode="live"):
        self.adapter = adapter
        self.mode = mode
        self.evidence_chain = []

    def answer(self, question, location="Phoenix, AZ", date_time=None):
        """Answer a heat question with planning, tool calls, and evidence."""
        self.evidence_chain = []

        # Step 1: Record user request
        self._add_evidence("user_request", {
            "question": question,
            "location": location,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

        # Step 2: Plan — question-dependent tool selection
        plan = plan_question(question)
        self._add_evidence("plan", {
            "interpreted_intent": plan["interpreted_intent"],
            "selected_tools": plan["selected_tools"],
            "rationale": plan["rationale"]
        })

        # Step 3: Execute plan
        heatmap_result = None
        env_result = None

        if "get_heatmap" in plan["selected_tools"]:
            heatmap_result = self._call_heatmap(location, date_time)
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
            # Select coordinate from global hottest feature
            candidates = heatmap_result.get("candidates_for_env_params", [])
            if not candidates:
                return self._error_answer("No temperature candidates found")

            selected = candidates[0]  # Global hottest
            self._add_evidence("coordinate_selection", {
                "selected_coordinate": selected,
                "selection_method": "global_maximum_temperature_feature",
                "observation_time": heatmap_result["observation_time"]
            })

            env_result = self._call_env_params(selected, date_time)
            if env_result is None:
                return self._error_answer("Environmental parameters call failed")

            self._add_evidence("env_params_result", {
                "tool": "get_environmental_parameters",
                "activity_id": env_result.get("activity_id"),
                "heat_index": env_result["result"]["heat_index_celsius"],
                "apparent_temp": env_result["result"]["apparent_temperature_celsius"],
                "humidity": env_result["result"]["relative_humidity_percent"],
                "observation_time": env_result["observation_time"],
                "mode": self.mode
            })

        # Step 4: Compose answer
        answer = self._compose_answer(heatmap_result, env_result, question, location, plan)
        return answer

    def _call_heatmap(self, location, date_time):
        if self.mode == "replay":
            return self._replay_heatmap()
        return self._live_heatmap(location, date_time)

    def _live_heatmap(self, location, date_time):
        request_params = {
            "polygon_aoi": {
                "type": "FeatureCollection",
                "features": [{
                    "type": "Feature",
                    "properties": {},
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[
                            [-112.08, 33.44],
                            [-112.06, 33.44],
                            [-112.06, 33.46],
                            [-112.08, 33.46],
                            [-112.08, 33.44]
                        ]]
                    }
                }]
            },
            "date_time": date_time or {
                "start_date": "2026-08-25",
                "start_time": "14:00",
                "filter_type": 1
            },
            "granularity": 100
        }
        try:
            raw = self.adapter.submit_heatmap(request_params)
            activity_id = raw.get("data", {}).get("activity_id")
            if not activity_id:
                return None
            status_result = self.adapter.poll_status(activity_id)
            status_data = status_result.get("data", {})
            if status_data.get("status") != "Completed":
                return None
            return normalize_heatmap_result(
                status_data, request_params, mode="live", activity_id=activity_id
            )
        except Exception:
            return None

    def _replay_heatmap(self):
        fixture_path = Path("fixtures/fortyguard/heatmap/phoenix-2026-08-25-14h.json")
        if not fixture_path.exists():
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
            "date_time": date_time or {
                "start_date": "2026-08-25",
                "start_time": "14:00",
                "filter_type": 1
            }
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
        fixture_path = Path("fixtures/fortyguard/env_params/phoenix-33.4484--112.0740-2026-08-25-14h.json")
        if not fixture_path.exists():
            return None
        with open(fixture_path) as f:
            raw = json.load(f)
        data = raw.get("data", {})
        request_params = {
            "latitude": 33.4484,
            "longitude": -112.0740,
            "temperature": 42.0,
            "date_time": {"start_date": "2026-08-25", "start_time": "14:00", "filter_type": 1}
        }
        return normalize_env_params_result(
            data, request_params, mode="replay",
            fixture_path=str(fixture_path),
            activity_id=data.get("activity_id")
        )

    def _compose_answer(self, heatmap, env_params, question, location, plan):
        hm = heatmap["result"] if heatmap else {}
        ep = env_params["result"] if env_params else {}

        # Measured result
        apparent_delta = None
        if ep.get("apparent_temperature_celsius") and ep.get("temperature_celsius"):
            apparent_delta = round(ep["apparent_temperature_celsius"] - ep["temperature_celsius"], 1)

        # Observation time from the tools
        obs_time = heatmap["observation_time"] if heatmap else (env_params["observation_time"] if env_params else None)

        return {
            "answer": {
                "summary": f"The queried area in {location} is experiencing very high thermal conditions.",
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
                    }
                },
                "why_this_answer": plan.get("rationale", ""),
                "sources": [
                    {
                        "provider": "FortyGuard",
                        "endpoint": s["endpoint"],
                        "mode": s["mode"],
                        "observation_time": s.get("observation_time"),
                        "activity_id": s.get("activity_id")
                    }
                    for s in self._collect_sources(heatmap, env_params)
                ],
                "mode": self.mode,
                "observation_time": obs_time
            },
            "evidence_chain": self.evidence_chain,
            "raw_results": {
                "heatmap": heatmap,
                "env_params": env_params
            }
        }

    def _collect_sources(self, heatmap, env_params):
        sources = []
        if heatmap:
            sources.append({
                "endpoint": "/v1/heatmap",
                "mode": heatmap["mode"],
                "observation_time": heatmap["observation_time"],
                "activity_id": heatmap.get("activity_id")
            })
        if env_params:
            sources.append({
                "endpoint": "/v1/env_params",
                "mode": env_params["mode"],
                "observation_time": env_params["observation_time"],
                "activity_id": env_params.get("activity_id")
            })
        return sources

    def _error_answer(self, message):
        return {
            "answer": {
                "summary": f"Unable to answer: {message}",
                "conditions": {},
                "why_this_answer": message,
                "sources": [],
                "mode": self.mode,
                "observation_time": None,
                "error": True
            },
            "evidence_chain": self.evidence_chain,
            "raw_results": {}
        }

    def _add_evidence(self, step, data):
        self.evidence_chain.append({
            "step": step,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
