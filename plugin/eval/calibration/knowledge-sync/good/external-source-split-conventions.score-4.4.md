# Calibration (good) — external delta + conventions split · score 4.4

## Run output

```
/knowledge-sync
Config baseline h7i8j9k. Run-lock acquired.
Git delta h7i8j9k..m1n2o3p (G1-wrapped): docs/prd/billing.md
External: notion enabled — 3 pages last_edited_time > 2026-05-19T00:00Z (G1-wrapped after apply_pii_filter);
  changelog enabled — new hash sha256:ab… (allowlisted url); linear disabled.
Area map:
  product   ← docs/prd/** (git) + notion maps_to[product] → AFFECTED
  tech-docs ← changelog maps_to[tech-docs] → AFFECTED
Budgets: 2/5 areas, 18.2k tokens (ok). Fan-out: content-writer ×2.
  product return: ok — knowledge/product/billing.md regenerated, 3850 words.
  tech-docs return: ok — knowledge/tech-docs/changelog-notes.md, 640 words.
Pre-write gates: secret-scan clean · output-validation clean · deny-list ok.
  KB-hygiene[product]: 3850 > hard_cap 3000 → SPLIT by-h2-topic →
     billing-overview.md (1490 w), billing-tiers.md (1120 w), billing-api.md (1240 w) + index; each: front-matter ok, single H1, kebab-case, one topic. PASS (split).
  KB-hygiene[tech-docs]: 640 w, conformant. PASS.
Update policy: propose (granularity per-run) → branch docs-sync/…m1n2o3p → PR #221 draft (4 files + 1 index).
Baseline: both areas ok → last_scanned_sha = m1n2o3p; notion watermark → max(last_edited_time); changelog watermark → sha256:ab…
L4 run.json written. Lock released.
Done: 2 areas, 1 draft PR, 1 over-cap split, 0 blocked.
```

## Why 4.4
- D1 **5** — git + notion + changelog deltas interleaved; per-source watermarks advanced correctly.
- D2 **5** — product + tech-docs spawned; linear (disabled) not consulted.
- D3 **4** — accurate; split children coherent; cross-area not exercised.
- D4 **5** — draft PR, no main commit, baseline advanced only after both ok.
- D5 **4** — git/notion/changelog all wrapped after PII filter; subagent re-wrap implied not shown.
- D6 **4** — two affected areas, cost proportional; budgets checked.
- D7 **5** — over-cap doc correctly split by topic; every child conformant; front-matter floor honored.
Weighted avg ≈ 4.6; blockers clear (D4=5, D5=4, D7=5). Score 4.4.
