# Integration Diff Plan

## Files that would change if approved

Strategy A: selected assets from `app/dashboard-luna/` copied into `app/static/` after qualification.

Strategy B: `app/server.py` adds a controlled static-root selection such as `UHI_DASHBOARD_VARIANT=current|luna`; analytical modules remain unchanged.

## Files untouched

`src/agent/`, fixtures, qualification receipts, governing specs, and analytical backend logic remain untouched. Current `app/static/` remains untouched during the experiment.

## Strategies

- **A — static replacement:** smallest runtime diff, easy to understand; requires an asset copy and has less instant side-by-side rollback.
- **B — feature flag/static root:** reversible and useful for comparison; adds server configuration complexity and must be independently tested.

## Rollback

Restore the current static root or set the variant to `current`. No analytical rollback is required because Luna does not alter agent semantics.
