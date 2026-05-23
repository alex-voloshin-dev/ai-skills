# Calibration (good) — no-change day early-exit · score 4.3

## Run output

```
/knowledge-sync
Config: knowledge/.knowledge-sync.yml (baseline e4f5g6h). Run-lock acquired (.lock).
Git delta e4f5g6h..e4f5g6h → empty (HEAD == last_scanned_sha).
External sources: changelog enabled — WebFetch https://example.com/changelog (allowlisted);
  content hash unchanged vs watermark sha256:9f2c… → no delta. linear/notion disabled (skipped).
Area map: affected = {} (no source change maps to any area).
No-change early-exit: no fan-out, no PR, no baseline bump.
L4: wrote .ai-skills-memory/knowledge-sync/2026-05-23T0800-e4f5g6h/run.json {status: no-change, areas: 0, tokens: 1.1k}.
Lock released.
Done: nothing to update.
```

## Why 4.3
- D1 Delta correctness **5** — empty git delta + unchanged changelog hash both detected correctly.
- D2 Area-targeting **5** — zero spawns; affected set empty.
- D3 Doc quality **n/a** — nothing generated; scored neutral (4) so it does not inflate or deflate.
- D4 Safety **5** — no write, no commit, baseline correctly NOT advanced past unprocessed work (nothing to advance).
- D5 Wrapping **4** — the WebFetch body that was compared was fetched under the allowlist; full wrap not needed since no agent reasoned over content.
- D6 Cost **5** — one git diff + one allowlisted WebFetch + one log line; no spawns. The model behavior the no-change guard is designed for.
- D7 Conventions **n/a** — no doc written; scored neutral (4).
Weighted avg ≈ 4.4; blockers clear (D4=5, D5=4, D7=4). Score 4.3 — exemplary cheap no-op, with two neutral dimensions.
