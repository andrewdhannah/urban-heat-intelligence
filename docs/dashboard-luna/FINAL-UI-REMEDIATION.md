# Final UI Remediation

Parent: `81bc88d4f5a98410b99ebf86ebc8082ed22753c9`

## Changes

- Park names now derive from `parks.inside_park.park_name`; no park and unavailable remain distinct.
- Live errors distinguish bounded freshness exhaustion from generic completion failure and preserve explicit Try Replay.
- Additive Luna browser assertions cover canonical Replay count, finite thermal legend, payload-derived park truth, representative Replay context, repeated Replay, keyboard controls, and evidence.

## Observed validation

- Luna Chromium suite: PASS.
- Replay payload: 367 features, three candidates, near-tie, Brief, evidence, NWS exclusion.
- Screenshots were preserved from the prior visual pass because these corrections did not alter the frozen layout.
- Historical suites: S1 20/20, S2 15/15, S3 hardening 12/12, S3B semantic 22/25 (three browser checks unavailable under repository interpreter), Level A GIS 44/44, Live mode 17/18 (one credential-consumption test failed because no credential was present), S2 browser and controlled-Live skipped because Playwright is unavailable to the repository interpreter.

## Limitations

The challenger remains based on the 3134f28 backend lineage. The separate EXP-A0 O19 backend remediation is not reconciled. No qualification or promotion claim is made.
