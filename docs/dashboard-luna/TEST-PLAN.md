# Test Plan

## Existing suites

Repository README lists `python3 tests/test_s1.py`, `test_s2.py`, `test_s2_browser.py`, and `test_s2_controlled_live.py`. These remain control/backend qualification suites and are not modified by Luna.

## Challenger checks

- Static shell and stable semantic hooks.
- Replay auto-request and visible historical mode/time.
- Live mode request and bounded failure without stale geometry.
- Payload-order candidate cards and marker sync.
- Near-tie callout without visual rank exaggeration.
- GIS context-only disclosure and unavailable wording.
- Replay NWS exclusion.
- Keyboard evidence drawer and candidate cards.
- Reduced-motion CSS and responsive overflow review.
- Security scan for credentials and unsafe DOM insertion.

## Current status

Implementation-level checks completed by source review. Browser execution, screenshot capture, axe audit, and repository test execution require a running backend/browser harness and remain pending independent QA. This challenger must not be described as qualified.
