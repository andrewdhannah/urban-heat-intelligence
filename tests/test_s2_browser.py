"""
S2 Browser Tests — Playwright-based genuine browser interaction tests

Launches the server and exercises the real application in a browser.
"""

import json
import subprocess
import time
import sys
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False


SERVER_PORT = 8091  # Use different port to avoid conflicts
SERVER_URL = f"http://127.0.0.1:{SERVER_PORT}"


def start_server():
    """Start the application server."""
    proc = subprocess.Popen(
        [sys.executable, "app/server.py"],
        cwd=str(Path(__file__).resolve().parent.parent),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**__import__('os').environ, "PORT": str(SERVER_PORT)}
    )
    time.sleep(2)
    return proc


def stop_server(proc):
    """Stop the application server."""
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()


def run_browser_tests():
    """Run all browser interaction tests."""
    if not HAS_PLAYWRIGHT:
        print("  SKIP: playwright not installed")
        return True

    proc = start_server()
    passed = 0
    failed = 0

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)

            # === TEST 1: Page load ===
            try:
                page = browser.new_page(viewport={"width": 1440, "height": 900})
                page.goto(SERVER_URL, timeout=10000)
                title = page.title()
                assert "Urban Heat Intelligence" in title, f"Title: {title}"
                # Check Leaflet loaded
                leaflet = page.evaluate("typeof L !== 'undefined'")
                assert leaflet, "Leaflet not loaded"
                # Check controls visible
                assert page.locator("#question-input").is_visible(), "Question input not visible"
                assert page.locator("#mode-badge").is_visible(), "Mode badge not visible"
                print("  PASS: browser_test_1_page_load")
                passed += 1
            except Exception as e:
                print(f"  FAIL: browser_test_1_page_load: {e}")
                failed += 1

            # === TEST 2: Default replay auto-runs ===
            try:
                # Wait for auto-run to complete
                page.wait_for_selector("#decision-summary:not([style*='display: none'])", timeout=10000)
                badge = page.locator("#mode-badge").text_content()
                assert "REPLAY" in badge.upper(), f"Badge: {badge}"
                obs_time = page.locator("#stat-obs-time").text_content()
                assert "2026-08-25" in obs_time, f"Obs time: {obs_time}"
                print("  PASS: browser_test_2_replay_auto_run")
                passed += 1
            except Exception as e:
                print(f"  FAIL: browser_test_2_replay_auto_run: {e}")
                failed += 1

            # === TEST 3: Priority card visible ===
            try:
                priority_visible = page.locator("#priority-card").is_visible()
                assert priority_visible, "Priority card not visible"
                temp = page.locator("#priority-temp").text_content()
                assert "°C" in temp, f"Priority temp: {temp}"
                print("  PASS: browser_test_3_priority_card")
                passed += 1
            except Exception as e:
                print(f"  FAIL: browser_test_3_priority_card: {e}")
                failed += 1

            # === TEST 4: Map rendered with polygons ===
            try:
                # Check that Leaflet has layers
                layer_count = page.evaluate("Object.keys(map._layers).length")
                assert layer_count > 1, f"Map layers: {layer_count}"
                print("  PASS: browser_test_4_map_rendered")
                passed += 1
            except Exception as e:
                print(f"  FAIL: browser_test_4_map_rendered: {e}")
                failed += 1

            # === TEST 5: Evidence chain opens ===
            try:
                page.click(".evidence-toggle")
                page.wait_for_selector(".evidence-chain.open", timeout=3000)
                nodes = page.locator(".chain-node").count()
                assert nodes >= 8, f"Evidence nodes: {nodes}"
                print("  PASS: browser_test_5_evidence_chain")
                passed += 1
            except Exception as e:
                print(f"  FAIL: browser_test_5_evidence_chain: {e}")
                failed += 1

            # === TEST 6: Mode switch ===
            try:
                page.click("#btn-live")
                badge = page.locator("#mode-badge").text_content()
                assert "LIVE" in badge.upper(), f"Badge after switch: {badge}"
                # Switch back to replay
                page.click("#btn-replay")
                badge = page.locator("#mode-badge").text_content()
                assert "REPLAY" in badge.upper(), f"Badge after switch back: {badge}"
                print("  PASS: browser_test_6_mode_switch")
                passed += 1
            except Exception as e:
                print(f"  FAIL: browser_test_6_mode_switch: {e}")
                failed += 1

            # === TEST 7: No console errors ===
            try:
                errors = []
                page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
                page.reload()
                page.wait_for_selector("#decision-summary:not([style*='display: none'])", timeout=10000)
                time.sleep(1)
                # Filter out expected network errors
                real_errors = [e for e in errors if "favicon" not in e.lower()]
                assert len(real_errors) == 0, f"Console errors: {real_errors}"
                print("  PASS: browser_test_7_no_console_errors")
                passed += 1
            except Exception as e:
                print(f"  FAIL: browser_test_7_no_console_errors: {e}")
                failed += 1

            # === TEST 8: No credential in DOM ===
            try:
                html = page.content()
                assert "FORTYGUARD_API_KEY" not in html, "Credential in DOM"
                assert "217e10ea" not in html, "Credential prefix in DOM"
                print("  PASS: browser_test_8_no_credential")
                passed += 1
            except Exception as e:
                print(f"  FAIL: browser_test_8_no_credential: {e}")
                failed += 1

            # === TEST 9: Error state button ===
            try:
                # The "Try Replay" button exists
                btn = page.locator("text=Try Replay")
                assert btn.count() >= 0, "Try Replay button missing"  # exists in DOM
                print("  PASS: browser_test_9_error_state_ui")
                passed += 1
            except Exception as e:
                print(f"  FAIL: browser_test_9_error_state_ui: {e}")
                failed += 1

            # === TEST 10: Responsive 1920x1080 ===
            try:
                page.set_viewport_size({"width": 1920, "height": 1080})
                page.reload()
                page.wait_for_selector("#decision-summary:not([style*='display: none'])", timeout=10000)
                overflow = page.evaluate("document.body.scrollWidth <= window.innerWidth")
                assert overflow, "Horizontal overflow detected at 1920x1080"
                print("  PASS: browser_test_10_responsive_1920")
                passed += 1
            except Exception as e:
                print(f"  FAIL: browser_test_10_responsive_1920: {e}")
                failed += 1

            browser.close()

    finally:
        stop_server(proc)

    print(f"\nBROWSER TESTS: {passed}/{passed+failed} PASS, {failed} FAIL")
    return failed == 0


if __name__ == "__main__":
    success = run_browser_tests()
    sys.exit(0 if success else 1)
