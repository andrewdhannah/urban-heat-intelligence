# Provider Lag Analysis — FortyGuard Publication Timing

**Date:** 2026-08-27
**Project:** urban-heat-intelligence
**Branch:** hackathon-expansion

---

## Observed Provider Behavior

### Data Availability Window

FortyGuard heatmap data is NOT immediately available for the current hour.
Testing on 2026-08-27 at 15:15 MST:

| Requested Hour | Features Returned | Status |
|----------------|-------------------|--------|
| 14:00 (1 hour ago) | 0 | Completed, no data |
| 13:00 (2 hours ago) | 0 | Completed, no data |
| 12:00 (3 hours ago) | 0 | Completed, no data |
| 11:00 (4 hours ago) | 0 | Completed, no data |
| 10:00 (5 hours ago) | 0 | Completed, no data |
| 2026-08-26 14:00 (yesterday) | 367 | Completed with data |

### Provider Publication Lag

**Minimum observed lag:** >5 hours for current-day data
**Evidence:** 2026-08-27 14:00 (1 hour prior to test) returned 0 features

**Maximum availability lag:** Not established
**Note:** We have not determined where availability begins between >5h and ~25h.

**Behavior:** FortyGuard appears to publish heatmap data with significant delay,
likely related to:
- Satellite data processing pipeline
- Quality assurance/quality control
- Aggregation across multiple data sources

### Selected Lookback Policy

**Window:** 12 hours (MAX_LOOKBACK_HOURS = 12)

**This is a bounded freshness/product policy, not a proven worst-case publication lag.**

**Rationale:**
1. **Deliberate freshness bound:** 12 hours is a deliberate product decision for acceptable data latency
2. **Observed lag >5h:** We know provider lag exceeds 5 hours, but haven't established the maximum
3. **Bounded policy:** If no usable data exists within 12 hours, report Live unavailable
4. **Fallback exists:** Replay mode provides deterministic alternative

**If genuine provider latency exceeds 12 hours:**
The bounded window will exhaust and return LIVE unavailable.
This is correct behavior - it surfaces the limitation rather than hiding it.

### Policy Definition

- **12 hours:** Bounded Live freshness window (product policy)
- **Observed lag:** >5 hours (evidence-backed)
- **Maximum lag:** Not established (would require extensive testing)
- **If no data within 12h:** Live unavailable, no Replay substitution

### Recommended Future Enhancement

If provider publication timing becomes more predictable:
- Reduce window to match actual lag
- Add time-of-day awareness (data may be available earlier in day)
- Consider caching latest successful observation time

---

*Provider lag analysis based on observed FortyGuard API behavior on 2026-08-27.*
