# Open Technical Decisions (SRS section 16) - proposed defaults

These are working defaults, not confirmed requirements. Please confirm or change them.

| # | Decision | Proposed default |
|---|----------|------------------|
| 1 | Game environment | Developer-controlled simulation / authorized test build only. Third-party live multiplayer is not assumed authorized. |
| 2 | Board layout | Square board, 4 corner pockets, derived from geometry (configurable). Rules in a separate config. |
| 3 | Capture | MediaProjection plus a prerecorded-frame test pipeline (same Module A interface). |
| 4 | Detection | Classical OpenCV first; ML only if measured insufficient. |
| 5 | Position error | Open: suggest <= 0.5% of board width. |
| 6 | Latency | Open: suggest median <= 100 ms, p95 <= 200 ms per frame, measured on documented hardware. |
| 7 | Calibration | Open: requires a controlled environment; parameters stay labelled uncalibrated until then. |
| 8 | Initial deliverable | Standalone physics library first (done as Python reference in `physics/`), then port to Kotlin. |
| 9 | Automation | Advisory only; no input injection. |

## Status
Implemented: `physics/geometry.py` (direct shots, single-cushion banks via pocket reflection,
blocked/impossible rejection, grazing test) with `physics/test_geometry.py` (9 tests passing:
`cd carrom/physics && python3 test_geometry.py`).
Not implemented: Android app, OpenCV vision, overlay, momentum/friction, ranking.
The Definition of Done in section 15 requires all of these.
Units are normalized board widths; shot power is uncalibrated.
