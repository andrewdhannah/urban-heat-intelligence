# Provenance UX

Luna has three disclosure levels:

- **Glanceable:** source label, mode, observation time, measured/context key.
- **Analytical:** candidate cards, Brief claim metadata, context-only disclosure.
- **Audit:** evidence drawer timeline showing actual events, repeated candidate steps, provider labels and timestamps.

FortyGuard is labeled “Decision evidence” and its heatmap/env results are marked used in decision. NWS claims are “context only”; Replay gets an explicit exclusion claim. GIS rows and claims are “context only” with `used_in_decision=false`. Future sources are not shown until payload integration and authorization.

Claims are rendered as readable text plus source/provider and use status. Raw JSON is not required for comprehension.
