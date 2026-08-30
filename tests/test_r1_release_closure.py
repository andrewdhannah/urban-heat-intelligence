import json
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


def test_public_live_get_is_rejected_without_provider_work():
    handler = object.__new__(server.UHIHandler)
    handler.path = "/api/answer?question=test&mode=live"
    handler.send_error = lambda status, message: setattr(handler, "rejection", (status, message))
    handler.send_response = lambda status: setattr(handler, "status", status)
    handler.send_header = lambda *args: None
    handler.end_headers = lambda: None
    handler.wfile = type("Writer", (), {"write": lambda self, value: setattr(handler, "body", value)})()
    with patch.object(server, "get_agent_result", side_effect=AssertionError("synchronous Live bypass")):
        server.UHIHandler.do_GET(handler)
    assert getattr(handler, "status", None) == 400
    assert b"/api/live/start" in handler.body


def test_live_start_is_the_provider_intensive_public_path():
    server.LIVE_JOBS.clear()
    handler = object.__new__(server.UHIHandler)
    handler.path = "/api/live/start"
    handler.headers = {"Content-Length": "18"}
    handler.rfile = type("Reader", (), {"read": lambda self, n: b'{"question":"test"}'})()
    handler.send_response = lambda status: setattr(handler, "status", status)
    handler.send_header = lambda *args: None
    handler.end_headers = lambda: None
    handler.wfile = type("Writer", (), {"write": lambda self, value: setattr(handler, "body", value)})()
    with patch.object(server.threading, "Thread") as thread:
        server.UHIHandler.do_POST(handler)
        thread.assert_called_once()
    assert handler.status == 202
    assert json.loads(handler.body)["job_id"]


def test_build_identity_prefers_render_commit(monkeypatch):
    monkeypatch.setenv("RENDER_GIT_COMMIT", "abc123")
    monkeypatch.setenv("GIT_COMMIT", "local")
    assert server.build_identity() == "abc123"
