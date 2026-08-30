import json
import threading
import time
from unittest.mock import patch

from app import server


def test_live_start_is_queued_and_worker_failure_is_contained():
    server.LIVE_JOBS.clear()

    def failing_agent(question, mode):
        time.sleep(0.05)
        raise RuntimeError("provider timeout")

    with patch.object(server, "get_agent_result", side_effect=failing_agent):
        job_id = "test-job"
        with server.LIVE_JOBS_LOCK:
            server.LIVE_JOBS[job_id] = {
                "job_id": job_id, "state": "queued", "stage": "queued",
                "provider_operation": None, "safe_error_class": None,
                "created_at": time.time(), "updated_at": time.time(),
                "finished_at": None, "payload": None,
            }
        thread = threading.Thread(target=server._run_live_job, args=(job_id, "test"))
        thread.start()
        thread.join(2)

    assert not thread.is_alive()
    assert server.LIVE_JOBS[job_id]["state"] == "failed"
    assert server.LIVE_JOBS[job_id]["safe_error_class"] == "RuntimeError"


def test_live_job_success_stores_sanitized_payload():
    server.LIVE_JOBS.clear()
    result = {"answer": {"mode": "live", "error": False}, "raw_results": {}, "evidence_chain": []}
    payload = {"mode": "live", "error": False, "heatmap": {"features": []}}
    with server.LIVE_JOBS_LOCK:
        server.LIVE_JOBS["success"] = {
            "job_id": "success", "state": "queued", "stage": "queued",
            "provider_operation": None, "safe_error_class": None,
            "created_at": time.time(), "updated_at": time.time(),
            "finished_at": None, "payload": None,
        }
    with patch.object(server, "get_agent_result", return_value=result), patch.object(server, "build_visualization_payload", return_value=payload):
        server._run_live_job("success", "test")
    assert server.LIVE_JOBS["success"]["state"] == "completed"
    assert server.LIVE_JOBS["success"]["payload"] == payload
    assert "api_key" not in json.dumps(server.LIVE_JOBS["success"])
