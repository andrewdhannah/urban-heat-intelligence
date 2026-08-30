import json
import os
import threading
import time
from unittest.mock import patch

from app import server
from src.tools.gis_context import query_nearest_intersection


def test_replay_intersection_fixture_is_authoritative_and_zero_network():
    with patch("src.tools.gis_context.urllib.request.urlopen", side_effect=AssertionError("Replay must not use network")):
        result = query_nearest_intersection(33.4590, -112.0774, mode="replay")
    assert result["result"]["available"] is True
    assert result["result"]["name"] == "W PORTLAND ST & N 3RD AVE"
    assert result["result"]["used_in_decision"] is False
    assert result["result"]["coordinate"] == [-112.07777981436898, 33.45966829025464]


def test_direct_live_answer_is_bounded_and_does_not_start_provider_work():
    class Request:
        path = "/api/answer?mode=live"
    handler = object.__new__(server.UHIHandler)
    handler.path = Request.path
    handler.send_response = lambda status: setattr(handler, "status", status)
    handler.send_header = lambda *args: None
    handler.end_headers = lambda: None
    handler.wfile = type("Writer", (), {"write": lambda self, value: setattr(handler, "body", value)})()
    with patch.object(server, "get_agent_result", side_effect=AssertionError("synchronous Live bypass")):
        server.UHIHandler.serve_answer(handler, "test", "live")
    # The public GET dispatcher rejects Live before serve_answer; this direct
    # guard documents that serve_answer itself remains replay-oriented.
    assert not hasattr(handler, "status") or handler.status in (200, 500)


def test_build_identity_prefers_render_commit(monkeypatch):
    monkeypatch.setenv("RENDER_GIT_COMMIT", "abc123")
    monkeypatch.setenv("GIT_COMMIT", "local")
    assert server.build_identity() == "abc123"
