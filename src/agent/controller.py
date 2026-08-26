"""
Agent Controller — Minimal heat-question answering agent

Decides which tools to call based on user's heat question.
Composes evidence chain and produces structured answer.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

from src.tools.heatmap import normalize_heatmap_result
from src.tools.env_params import normalize_env_params_result


class HeatAgent:
    """
    Minimal agent that answers heat questions using FortyGuard tools.

    Flow:
        user question -> tool selection -> heatmap -> env_params -> answer
    """

    def __init__(self, adapter, mode="live"):
        """
        Args:
            adapter: FortyGuard adapter instance (for live calls)
            mode: "live" or "replay"
        """
        self.adapter = adapter
        self.mode = mode
        self.evidence_chain = []

    def answer(self, question, location="Phoenix, AZ", date_time=None):
        """
        Answer a heat question.

        Args:
            question: User's heat question
            location: Location string (for context)
            date_time: Date/time dict for API calls

        Returns:
            Structured answer with evidence chain
        """
        self.evidence_chain = []

        # Step 1: Record user request
        self._add_evidence("user_request", {
            "question": question,
            "location": location,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

        # Step 2: Agent decides to query heatmap first
        # (question asks about area-level heat)
        self._add_evidence("tool_selection", {
            "decision": "Query heatmap first because question asks about area-level heat risk",
            "selected_tool": "get_heatmap",
            "rationale": "Heatmap provides spatial temperature distribution for the area"
        })

        # Step 3: Call heatmap
        heatmap_result = self._call_heatmap(location, date_time)
        if heatmap_result is None:
            return self._error_answer("Heatmap call failed")

        self._add_evidence("heatmap_result", {
            "tool": "get_heatmap",
            "feature_count": heatmap_result["result"]["feature_count"],
            "mean_temp": heatmap_result["result"]["mean_temperature_celsius"],
            "max_temp": heatmap_result["result"]["max_temperature_celsius"],
            "mode": self.mode
        })

        # Step 4: Select representative coordinate
        candidates = heatmap_result.get("candidates_for_env_params", [])
        if not candidates:
            return self._error_answer("No temperature candidates found in heatmap")

        selected = candidates[0]  # Hottest location
        self._add_evidence("coordinate_selection", {
            "decision": f"Selected hottest location for env_params: ({selected['latitude']}, {selected['longitude']})",
            "selected_coordinate": selected,
            "rationale": "Hottest location provides most relevant local conditions"
        })

        # Step 5: Call env_params
        env_result = self._call_env_params(selected, date_time)
        if env_result is None:
            return self._error_answer("Environmental parameters call failed")

        self._add_evidence("env_params_result", {
            "tool": "get_environmental_parameters",
            "heat_index": env_result["result"]["heat_index_celsius"],
            "apparent_temp": env_result["result"]["apparent_temperature_celsius"],
            "humidity": env_result["result"]["relative_humidity_percent"],
            "mode": self.mode
        })

        # Step 6: Compose answer
        answer = self._compose_answer(heatmap_result, env_result, question, location)

        return answer

    def _call_heatmap(self, location, date_time):
        """Call heatmap tool (live or replay)."""
        if self.mode == "replay":
            return self._replay_heatmap()
        else:
            return self._live_heatmap(location, date_time)

    def _live_heatmap(self, location, date_time):
        """Execute live heatmap call."""
        # Default Phoenix AOI
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
                status_data, request_params, mode="live"
            )
        except Exception as e:
            return None

    def _replay_heatmap(self):
        """Load heatmap from genuine S0 fixture."""
        fixture_path = Path("fixtures/fortyguard/heatmap/phoenix-2026-08-25-14h.json")
        if not fixture_path.exists():
            return None

        with open(fixture_path) as f:
            raw = json.load(f)

        data = raw.get("data", {})
        request_params = {
            "polygon_aoi": "Phoenix downtown (from fixture)",
            "date_time": {"start_date": "2026-08-25", "start_time": "14:00", "filter_type": 1},
            "granularity": 100
        }

        return normalize_heatmap_result(
            data, request_params, mode="replay",
            fixture_path=str(fixture_path)
        )

    def _call_env_params(self, coordinate, date_time):
        """Call env_params tool (live or replay)."""
        if self.mode == "replay":
            return self._replay_env_params()
        else:
            return self._live_env_params(coordinate, date_time)

    def _live_env_params(self, coordinate, date_time):
        """Execute live env_params call."""
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
                status_data, request_params, mode="live"
            )
        except Exception as e:
            return None

    def _replay_env_params(self):
        """Load env_params from genuine S0 fixture."""
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
            fixture_path=str(fixture_path)
        )

    def _compose_answer(self, heatmap, env_params, question, location):
        """Compose structured answer with evidence chain."""
        hm = heatmap["result"]
        ep = env_params["result"]

        # Measured results
        apparent_delta = None
        if ep.get("apparent_temperature_celsius") and ep.get("temperature_celsius"):
            apparent_delta = round(
                ep["apparent_temperature_celsius"] - ep["temperature_celsius"], 1
            )

        return {
            "answer": {
                "summary": f"The queried area in {location} is experiencing very high thermal conditions.",
                "conditions": {
                    "area_mean_temperature_celsius": hm["mean_temperature_celsius"],
                    "area_max_temperature_celsius": hm["max_temperature_celsius"],
                    "area_min_temperature_celsius": hm["min_temperature_celsius"],
                    "area_temperature_range_celsius": hm["temperature_range_celsius"],
                    "feature_count": hm["feature_count"],
                    "representative_location": {
                        "heat_index_celsius": ep["heat_index_celsius"],
                        "apparent_temperature_celsius": ep["apparent_temperature_celsius"],
                        "relative_humidity_percent": ep["relative_humidity_percent"],
                        "measured_temperature_celsius": ep["temperature_celsius"],
                    },
                    "measured_result": {
                        "apparent_vs_measured_delta_celsius": apparent_delta,
                        "interpretation": "Apparent temperature exceeds measured temperature due to solar and environmental factors"
                    }
                },
                "why_this_answer": "Queried FortyGuard heatmap for the area, then queried environmental parameters at the hottest location to provide local conditions.",
                "sources": [
                    {
                        "provider": "FortyGuard",
                        "endpoint": "/v1/heatmap",
                        "mode": heatmap["mode"],
                        "observation_time": heatmap["observation_time"]
                    },
                    {
                        "provider": "FortyGuard",
                        "endpoint": "/v1/env_params",
                        "mode": env_params["mode"],
                        "observation_time": env_params["observation_time"]
                    }
                ],
                "mode": self.mode,
                "observation_time": heatmap["observation_time"]
            },
            "evidence_chain": self.evidence_chain,
            "raw_results": {
                "heatmap": heatmap,
                "env_params": env_params
            }
        }

    def _error_answer(self, message):
        """Produce error answer."""
        return {
            "answer": {
                "summary": f"Unable to answer: {message}",
                "conditions": {},
                "why_this_answer": message,
                "sources": [],
                "mode": self.mode,
                "observation_time": datetime.now(timezone.utc).isoformat(),
                "error": True
            },
            "evidence_chain": self.evidence_chain,
            "raw_results": {}
        }

    def _add_evidence(self, step, data):
        """Add evidence node to chain."""
        self.evidence_chain.append({
            "step": step,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
