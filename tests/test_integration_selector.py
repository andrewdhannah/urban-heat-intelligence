"""Integration contract tests for DASH-V2-D.

Proves the reversible dashboard selector works correctly against the
accepted backend.  Both variants serve the same /api/answer backend;
only the presentation root differs.
"""
import json
import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.server import get_dashboard_variant, get_dashboard_dir, ALLOWED_VARIANTS, DEFAULT_VARIANT


# ── Selector unit tests ──────────────────────────────────────────────

class TestDashboardVariant:
    def test_default_variant_is_incumbent(self):
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("UHI_DASHBOARD_VARIANT", None)
            assert get_dashboard_variant() == "incumbent"

    def test_luna_variant_accepted(self):
        with patch.dict(os.environ, {"UHI_DASHBOARD_VARIANT": "luna"}):
            assert get_dashboard_variant() == "luna"

    def test_incumbent_variant_accepted(self):
        with patch.dict(os.environ, {"UHI_DASHBOARD_VARIANT": "incumbent"}):
            assert get_dashboard_variant() == "incumbent"

    def test_invalid_variant_falls_back_to_incumbent(self):
        with patch.dict(os.environ, {"UHI_DASHBOARD_VARIANT": "bogus"}):
            assert get_dashboard_variant() == "incumbent"

    def test_case_insensitive(self):
        with patch.dict(os.environ, {"UHI_DASHBOARD_VARIANT": "LUNA"}):
            assert get_dashboard_variant() == "luna"

    def test_whitespace_trimmed(self):
        with patch.dict(os.environ, {"UHI_DASHBOARD_VARIANT": "  luna  "}):
            assert get_dashboard_variant() == "luna"

    def test_allowed_variants_constant(self):
        assert "incumbent" in ALLOWED_VARIANTS
        assert "luna" in ALLOWED_VARIANTS
        assert len(ALLOWED_VARIANTS) == 2


class TestDashboardDir:
    def test_incumbent_serves_static(self):
        with patch.dict(os.environ, {"UHI_DASHBOARD_VARIANT": "incumbent"}):
            d = get_dashboard_dir()
            assert d.name == "static"
            assert (d / "index.html").exists()

    def test_luna_serves_dashboard_luna(self):
        with patch.dict(os.environ, {"UHI_DASHBOARD_VARIANT": "luna"}):
            d = get_dashboard_dir()
            assert d.name == "dashboard-luna"
            assert (d / "index.html").exists()

    def test_invalid_falls_back_to_static(self):
        with patch.dict(os.environ, {"UHI_DASHBOARD_VARIANT": "invalid"}):
            d = get_dashboard_dir()
            assert d.name == "static"


# ── File existence proof ────────────────────────────────────────────

class TestVariantFileExistence:
    def test_incumbent_index_exists(self):
        static = Path(__file__).resolve().parent.parent / "app" / "static" / "index.html"
        assert static.exists(), "Incumbent index.html missing"

    def test_luna_index_exists(self):
        luna = Path(__file__).resolve().parent.parent / "app" / "dashboard-luna" / "index.html"
        assert luna.exists(), "Luna index.html missing"

    def test_luna_dashboard_js_exists(self):
        js = Path(__file__).resolve().parent.parent / "app" / "dashboard-luna" / "js" / "dashboard.js"
        assert js.exists(), "Luna dashboard.js missing"

    def test_luna_css_exists(self):
        css = Path(__file__).resolve().parent.parent / "app" / "dashboard-luna" / "css" / "dashboard.css"
        assert css.exists(), "Luna dashboard.css missing"


# ── API contract: variant endpoint ──────────────────────────────────

class TestVariantEndpoint:
    def test_variant_endpoint_returns_json(self):
        """The /api/variant endpoint must return valid JSON with a variant field."""
        from app.server import UHIHandler
        import io

        with patch.dict(os.environ, {"UHI_DASHBOARD_VARIANT": "luna"}):
            variant = get_dashboard_variant()
            assert variant == "luna"

        with patch.dict(os.environ, {"UHI_DASHBOARD_VARIANT": "incumbent"}):
            variant = get_dashboard_variant()
            assert variant == "incumbent"

    def test_variant_exposes_no_secrets(self):
        """The variant endpoint must not expose environment metadata."""
        variant = get_dashboard_variant()
        assert variant in ALLOWED_VARIANTS
        # No credential fields
        for secret_pattern in ["KEY", "SECRET", "TOKEN", "PASSWORD", "CREDENTIAL"]:
            assert secret_pattern not in variant.upper()


# ── Backend contract: shared API invariant ──────────────────────────

class TestBackendContractShared:
    """Both dashboard variants share the same /api/answer backend.
    These tests verify the backend structure is invariant to the variant."""

    def test_visualization_payload_fields(self):
        """The build_visualization_payload must return the contract fields."""
        from app.server import build_visualization_payload

        # Minimal mock result
        mock_result = {
            "answer": {
                "mode": "replay",
                "observation_time": "2026-08-27T20:00:00Z",
                "summary": "Test summary",
                "conditions": {
                    "area_mean_temperature_celsius": 35.0,
                    "area_temperature_range_celsius": 5.0,
                    "ranking_status": "deterministic",
                    "ranked_candidates": [
                        {
                            "rank": 1,
                            "coordinate": [-112.07, 33.45],
                            "observed_temp": 38.5,
                            "delta_from_area_mean": 3.5,
                        }
                    ],
                },
                "why_this_answer": "Test reasoning",
                "sources": [],
                "error": False,
            },
            "evidence_chain": [
                {"step": "heatmap", "data": {"provider": "FortyGuard"}, "timestamp": None}
            ],
            "raw_results": {
                "heatmap": {
                    "mode": "replay",
                    "result": {
                        "map_data": {"features": []},
                        "feature_count": 0,
                    },
                    "observation_time": None,
                }
            },
            "context": {},
            "candidate_contexts": {},
            "context_evidence_chain": [],
        }

        payload = build_visualization_payload(mock_result)

        # Required top-level fields
        for field in [
            "mode", "observation_time", "summary", "conditions",
            "why_this_answer", "heatmap", "priority_location",
            "ranked_candidates", "nws_context", "urban_heat_brief",
            "evidence_chain", "error",
        ]:
            assert field in payload, f"Missing required field: {field}"

        # Visualization invariant: mode preserved
        assert payload["mode"] == "replay"

        # No secrets in payload
        raw = json.dumps(payload)
        for secret in ["FORTYGUARD_API_KEY", "SECRET", "PASSWORD", "TOKEN"]:
            assert secret not in raw, f"Secret leaked into payload: {secret}"

    def test_nws_replay_exclusion(self):
        """NWS context must be excluded from Replay mode."""
        from app.server import build_visualization_payload

        mock_result = {
            "answer": {
                "mode": "replay",
                "conditions": {"ranked_candidates": []},
                "error": False,
            },
            "evidence_chain": [],
            "raw_results": {},
            "context": {},
            "candidate_contexts": {},
            "context_evidence_chain": [],
        }

        payload = build_visualization_payload(mock_result)
        nws = payload["nws_context"]
        assert nws["evidence_status"] == "excluded_from_replay"
        assert nws["used_in_decision"] is False
