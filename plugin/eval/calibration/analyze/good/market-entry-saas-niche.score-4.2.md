# Analysis — Should we enter the AI-assisted code-review market?

> Question: viability of launching an AI code-review SaaS targeted at mid-market dev teams (50-500 engineers).
> Frameworks applied: Porter's Five Forces (primary), JTBD (secondary)
> Date: 2026-04-24

## Executive Summary

**FACT:** TAM for code-review tooling at our segment is ~$1.8B (2025), growing 22%/yr (source: Gartner Forecast Analysis: DevOps Tools 2025-2029, Q4 2025).
**INFERENCE:** Competitive intensity is HIGH and accelerating; differentiation must be narrow (one specific JTBD owned end-to-end), not broad-feature parity. MEDIUM confidence on the differentiation thesis.
**RECOMMENDATION:** Conditional GO — enter with a narrowly-scoped wedge (security-review-as-a-PR-comment) targeted at regulated industries; do not enter as general-purpose AI code review. Confidence: MEDIUM.

## Decomposition (MECE)

1. Market size + growth (TAM / SAM / SOM)
2. Competitive structure (Five Forces)
3. Buyer pain hierarchy (JTBD)
4. Build vs partner economics
5. Go-to-market path

## Porter's Five Forces

| Force | Rating | Evidence |
|---|---|---|
| Rivalry | HIGH | 8 well-funded incumbents (GitHub Copilot Reviews, Coderabbit, Greptile, Sourcery, Codium, Sonar, Cody, Tabnine Review). Source: Crunchbase + product launches Q1-Q4 2025 |
| Buyer power | MEDIUM-HIGH | Switching cost is low (CI integration only); buyers run pilots across 2-3 vendors as standard |
| Supplier power | HIGH | LLM API margins squeezed at the long tail; foundation-model vendors capture most value (source: Anthropic + OpenAI pricing trajectory 2024-2026) |
| Threat of new entrants | HIGH | Low technical moat for general code review; differentiation by data/distribution rather than tech |
| Substitutes | MEDIUM | Manual review + linters remain the default; LLM-augmented IDE tools (Cursor, Copilot) absorb some demand inside the IDE |

Net: the broad market is unattractive. Need a wedge where one or two forces are favourable.

## JTBD Analysis

Spoke to 12 engineering leaders at target companies (recordings: `interviews/2026-04/`). Three distinct jobs surfaced:

| Job | Pain (1-5) | Frequency | Current alternative | Notes |
|---|---|---|---|---|
| "Catch security bugs before merge" | 4.6 | per-PR | Snyk + manual | Regulated industries cited compliance pressure |
| "Speed up PR review cycle time" | 3.8 | per-PR | Manual reviewer | Cursor/Copilot eat into this; less urgent |
| "Enforce style/architecture conventions" | 2.9 | per-PR | Linters + custom rules | Solved-enough |

**Wedge candidate:** Job 1 (security review as a PR comment) — highest pain, weakest current alternative, regulated buyers willing to pay 3-5× the per-seat baseline.

## Build vs Partner

- BUILD: 18 engineering-months to MVP, ~$2.4M to first revenue
- PARTNER (white-label a security-engine, OEM into our review wrapper): 4 months to MVP, ~$0.6M to first revenue, lower margin

**Recommendation:** Partner first; build later only if margin pressure forces it.

## Risks

| Risk | P × I | Mitigation |
|---|---|---|
| Incumbent (e.g., GitHub) ships native equivalent | M × H | Lean into compliance/auditability features GitHub won't prioritize for 18+ months |
| LLM costs erode margin | M × H | Caching strategy + per-customer rate limits; renegotiate quarterly |
| Sales cycle in regulated industries is 9-12 months | H × M | Land 3 design partners pre-launch; budget reflects this |

## Confidence + Sensitivity

- HIGH on market size + competitive intensity
- MEDIUM on JTBD ranking (n=12 is small; would re-confirm at n=30 before committing)
- LOW-MEDIUM on the partner thesis (partner economics depend on which security-engine vendor)

## Out of Scope (deferred)

- Detailed financial model → finance team (separate)
- Product feature design for the wedge → `/feature-design` if we proceed
- Architecture for the security-engine integration → `/architecture` once feature design lands
