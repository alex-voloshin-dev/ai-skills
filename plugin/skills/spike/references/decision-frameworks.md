# Decision Frameworks for Spike Recommendations

Structured lenses for synthesizing a spike into a go / no-go / needs-more-info recommendation. Apply these in Step 4 (Synthesize) of the spike pipeline. Use multiple frameworks together — Cynefin tells you what kind of problem you have, One-Way/Two-Way tells you how reversible the call is, ICE/RICE ranks options when more than one path looks viable, and the Bezos 70% rule sets the cutoff for "needs more spike."

## Cynefin Framework (Dave Snowden)

Classify the problem before choosing an approach. Each domain has a different decision pattern and a different acceptable failure boundary.

| Domain | Cause-effect | Pattern | Practice | Spike fit | Acceptable failure |
|---|---|---|---|---|---|
| **Clear** | obvious | Sense → Categorize → Respond | best practice | usually unnecessary — apply known answer | none; do not experiment with solved problems |
| **Complicated** | knowable with expertise | Sense → Analyze → Respond | good practice | valuable for evaluating expert recommendations against your context | bounded — failure costs effort, not safety |
| **Complex** | known only in retrospect | Probe → Sense → Respond | emergent practice | **strong fit** — small safe-to-fail experiments | safe-to-fail by design; the experiment must be cheap to abandon |
| **Chaotic** | none | Act → Sense → Respond | novel practice | stabilize first; spike comes later | high — but speed of action dominates |
| **Confusion** | you do not know which domain you are in | break the problem apart | — | spike each piece into its own domain | n/a |

**Mapping spike type to framework:**

- "Can we use technology X?" → usually Complicated. Spike validates expert claims against your stack.
- "Best way to implement real-time sync at scale?" → usually Complex. Spike probes with a POC, observes, then decides.
- "Production is on fire — what now?" → Chaotic. Stabilize, then spike on the underlying cause after.
- "Should we adopt this pattern?" → could be any domain. Classify first, then choose spike depth.

## One-Way / Two-Way Doors (Bezos)

From the 1997 Amazon shareholder letter, reinforced in 2015 and 2016. Distinguishes reversibility class of the decision a spike is informing.

- **Two-way doors** — reversible decisions, costs to reverse are bounded. Make fast. Delay is the dominant cost. Per Bezos, roughly 70% of decisions are two-way and should be made by individuals or small groups with high judgment and high speed.
- **One-way doors** — irreversible or high cost-of-reversal. Make slow. Multi-perspective review, methodical, consultative. Examples: technology stack on a 2-year project, vendor lock-in with data egress fees, breaking API contracts, public schema changes, choice of primary database.
- **Recommendation per spike**: classify the spike's recommendation as one of:
  - `go-two-way` — recommend proceed; reversible if wrong; commit and learn.
  - `go-one-way` — recommend proceed; treat as committed; require additional sign-off, ARD, and rollback plan.
  - `needs more spike before commit` — too one-way to commit on current evidence; identify the specific gaps.

## ICE Scoring (Sean Ellis)

Use when the spike yields more than one viable path and you need to prioritize which to try first.

- **Impact** (1–10): expected value if it works.
- **Confidence** (1–10): how sure are we about the impact estimate (this is where evidence quality from `evidence-hierarchy.md` feeds in).
- **Ease** (1–10): effort to implement; 10 = easiest.
- **Score** = Impact × Confidence × Ease. Top score is first to try.

ICE is intentionally cheap. It is a tie-breaker, not a rigorous forecast. If two options score within ~15% of each other, treat them as tied and pick on qualitative grounds.

## RICE Scoring (Intercom)

Variant of ICE for feature-style prioritization where audience size matters.

- **Reach**: how many users / requests / events affected per time window.
- **Impact**: per-event or per-user impact (often a 0.25 / 0.5 / 1 / 2 / 3 scale).
- **Confidence**: percentage (50 / 80 / 100).
- **Effort**: person-weeks (or person-days for spike-scale).
- **Score** = Reach × Impact × Confidence / Effort.

Use RICE over ICE when the spike's recommendation depends on traffic / audience scale (e.g., "is this caching layer worth it?"), and ICE when it does not (e.g., "which gRPC client library?").

## Bezos 70% Rule

> "Most decisions should probably be made with somewhere around 70% of the information you wish you had. If you wait for 90%, in most cases, you're probably being slow."
> — Jeff Bezos, 2016 shareholder letter

Apply to the "needs more spike" branch:

- If you have ≥70% of the information you would want and the door is two-way → recommend `go-two-way`.
- If you have <70% and the door is one-way → recommend `needs more spike before commit`, list the specific gaps.
- If you have <70% but the door is two-way → still consider `go-two-way` with explicit "reversal plan if wrong" — speed of learning outweighs the missing 30%.

## Decision Recommendation Lens for Spike Report

For each option the spike surfaces, classify on four axes and then recommend:

1. **Cynefin domain** — Clear / Complicated / Complex / Chaotic / Confusion.
2. **Reversibility** — one-way / two-way (with rough cost-of-reversal estimate).
3. **ICE or RICE relative score** — vs. the other options on the table.
4. **Confidence level** — drawn from `evidence-hierarchy.md` source levels (level 1–4 = high; level 5 = medium; level 6–7 = low).

Then express the recommendation as:

> Option A (Cynefin: Complicated, two-way door, ICE 240, confidence: high from level-2 evidence) → **go-two-way**, proceed with prototype.
> Option B (Cynefin: Complex, one-way door, ICE 180, confidence: medium from level-3 evidence) → **needs more spike before commit**, gap is production-load behavior.

This makes the recommendation auditable and reviewable rather than a single bare verdict.
