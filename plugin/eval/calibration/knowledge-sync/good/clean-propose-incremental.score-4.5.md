# Calibration (good) — clean propose-only incremental run · score 4.5

## Run output

```
/knowledge-sync
Path B (Agent Teams) team-create attempted… ok.
Config: knowledge/.knowledge-sync.yml (baseline a1b2c3d). Run-lock acquired (.lock).
Git delta a1b2c3d..e4f5g6h (read-only git diff, G1-wrapped):
  src/api/routes.ts, src/api/handlers.ts
External sources: linear enabled — 0 issues since watermark 2026-05-20T08:00Z (no delta); notion disabled (skipped).
Area map (doc_areas[*].sources globs):
  tech-docs ← src/**  → AFFECTED (2 files)
  product   ← docs/prd/**  → unaffected (no spawn)
  marketing ← marketing/**  → unaffected (no spawn)
Budgets: 1/5 areas, projected 9.4k tokens (< per-run 50k, < per-day 200k). OK.
Fan-out: Agent(content-writer) ×1 [tech-docs] (role_hint: backend-engineer).
  return: ok — knowledge/tech-docs/api-routes.md updated (1180 words).
Pre-write gates: secret-scan (C3) clean · output-validation (C3b) clean · deny-list (C4) ok ·
  KB-hygiene: front-matter ok (title/area/owner/last_reviewed/source_refs), 1180 ≤ 3000, single H1, kebab-case, one topic. PASS.
Update policy: propose → branch docs-sync/2026-05-23T0800-e4f5g6h → /create-pr --draft --base main → PR #214 (draft).
Baseline: all areas ok → last_scanned_sha = e4f5g6h; linear watermark unchanged (no delta).
L4: .ai-skills-memory/knowledge-sync/2026-05-23T0800-e4f5g6h/run.json written. Lock released.
Done: 1 area updated, 1 draft PR, 0 blocked.
```

## Why 4.5
- D1 Delta correctness **5** — git delta correct; external (linear) consulted, zero-delta handled; watermark untouched.
- D2 Area-targeting **5** — only tech-docs spawned; product/marketing skipped; no-spawn noted.
- D3 Doc quality **4** — accurate, in-scope; cross-area consistency not exercised (single area).
- D4 Safety **5** — draft PR, no commit to main; baseline advanced only after the area returned ok; budgets enforced.
- D5 Wrapping **4** — diff + external return G1-wrapped; subagent-return re-wrap not explicitly shown in the log.
- D6 Cost **5** — one area, cost proportional, budgets checked.
- D7 Conventions **5** — front-matter, size, H1, naming, one-topic all verified pre-write.
Weighted avg ≈ 4.7; all blockers (D4=5, D5=4, D7=5) clear. Score set to 4.5 for the unshown subagent-return re-wrap detail.
