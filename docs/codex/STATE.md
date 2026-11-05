# Codex state

Updated: 2026-11-05

## Current objective / completed
- Fixed `python run_viewer.py` launch: stale Parcel cache referenced nonexistent sources.js despite current source imports.
- Each launch now uses a temporary session cache; child exit status propagates. Updated existing usage/report and added launcher regression.

## Verified
- Actual fixed launcher built successfully (1.09 s); viewer and /api/health each returned HTTP 200. Verification servers stopped.
- Launcher regression: 1 passed in tms312; full suite not repeated for this focused change.
- Prior rendering/QC acceptance and clinical-validation limits remain as documented in positional report/log. No subject data in checkpoints.

## Decisions / assumptions
- Session-local Parcel cache avoids obsolete graph reuse across source updates; incremental caching remains during a session.
- Python and npm use micromamba tms312. Sandbox verification requires writable cache paths and authorization for loopback binding.

## Uncommitted changes / blockers / next actions
- This task's launcher, test and documentation changes prepared for [codex] commit; see Git for delivery status.
- No unrelated changes at start. No implementation blocker. Prior external push rejection recorded in LOG; verify current delivery directly.
- Start with `micromamba run -n tms312 python run_viewer.py` and open http://127.0.0.1:1234.
- Delivery saved locally in c7ab497 (checkpoint follow-up follows). Push blocked by automatic approval review: unverified remote/private-code publication risk; requires user approval of destination. No push retry.
