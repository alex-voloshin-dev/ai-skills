# Optimizing Skill Descriptions

Faithful digest of https://agentskills.io/skill-creation/optimizing-descriptions
— the cached source of truth for the skill `description` (the entire
triggering surface). Read by `/plugin-author audit --deep`, `/plugin-author
improve`, and the `prompt-engineer` agent when a skill mis-triggers or its
description needs tuning. Re-fetch the live page when network is available;
otherwise these cached rules apply.

The `description` carries the **entire triggering burden** — under progressive
disclosure only `name` + `description` are loaded at startup for every skill.
If the description doesn't match the task, the skill body is never loaded.

Nuance: agents typically only consult skills for tasks needing knowledge or
capability beyond what they handle alone. A one-step "read this PDF" may not
trigger even with a perfect description. Specialized knowledge / unfamiliar
API / domain workflow / uncommon format is where a good description matters.

---

## Writing effective descriptions

- **Use imperative phrasing** — "Use this skill when…" not "This skill
  does…".
- **Focus on user intent, not implementation** — match what the user asked
  for, not internal mechanics.
- **Err on the side of being pushy** — explicitly list contexts, including
  ones where the user does not name the domain ("even if they don't
  explicitly mention 'CSV' or 'analysis'").
- **Keep it concise** — a few sentences to a short paragraph; hard limit
  **1024 chars**.

---

## Trigger eval queries

Build **~20 queries**: **8–10 should-trigger** + **8–10 should-not-trigger**.

Should-trigger queries — vary:
- phrasing (formal / casual / typos)
- explicitness (named vs unnamed domain)
- detail (terse vs context-heavy)
- complexity (single-step vs multi-step)

Most useful = cases where the skill helps but the connection is not obvious.

Should-not-trigger queries — the valuable negatives are **near-misses**
(share keywords but need something different), not obviously-irrelevant ones.

Realism: include file paths, personal context, specific details, casual
language / abbreviations / typos.

---

## Testing

- Run each query through the agent with the skill installed; observe whether
  it invoked the skill (loaded `SKILL.md`).
- Pass: `should_trigger == true` & invoked, OR `should_trigger == false` &
  not invoked.
- Nondeterministic → run each query multiple times (**3** reasonable);
  compute the **trigger rate**. Should-trigger passes if rate > threshold
  (**0.5** default); should-not passes if rate < threshold.
- 20 queries × 3 = **60 invocations** — script it.

---

## Train / validation split

- Train **~60%** (guides changes), validation **~40%** (checks
  generalization).
- Proportional mix of positive/negative in both splits.
- Fixed split across iterations.

---

## Optimization loop

1. Evaluate on train + validation.
2. Identify train failures.
3. Revise:
   - too-narrow ⇒ broaden
   - false-trigger ⇒ add specificity / boundaries
   - avoid keyword overfitting — address the general category, not one phrase
   - check ≤ **1024** chars
4. Repeat until train passes / no improvement.
5. Select the best iteration by **validation** pass rate (not necessarily the
   last). **~5 iterations** is usually enough.

Apply: update the description, verify ≤ 1024 chars, sanity-check with fresh
held-out queries.

Before / after example:
- Before: `description: Process CSV files.`
- After: `description: Analyze CSV and tabular data files — compute summary
  statistics, add derived columns, generate charts, and clean messy data. Use
  this skill when the user has a CSV, TSV, or Excel file and wants to explore,
  transform, or visualize the data, even if they don't explicitly mention
  "CSV" or "analysis."`

The `skill-creator` Skill (github.com/anthropics/skills) automates this loop.

---

## ai-skills overlay (additive, never weaker than upstream)

- Description in **third person** — first-person ("I help…") breaks discovery.
- **Form A (mandatory leading phrase):** every description **BEGINS with the
  literal phrase `Use this skill when `** (capital `U`; the four words
  `Use this skill when` then a space), followed by *when/why* the user (or,
  for knowledge skills, the agent) would invoke it. This is the ai-skills
  **strict operationalization** of upstream's "imperative phrasing" — upstream
  *recommends* `Use this skill when…` somewhere in the description; the
  ai-skills overlay *requires* it as the first token. The capability
  ("…to <do X>" / "…for <Y>") is **folded into the same description** — no
  information is lost versus the older capability-lead form. Stay third
  person, ≤ 1024 chars, and keep triggering/disambiguation keywords.
- The literal token **`TODO`** in a description is a CRITICAL audit fail
  (guards unedited `/plugin-author create` scaffolds).
- 1024-char hard limit is enforced by `plugin/dev/validate.py` — never exceed.
- Eval-first: do not change a triggering description without a measurement
  rationale (trigger-rate before/after on the ~20-query set).
- Companion spec digest: `skill-authoring-spec.md` (same dir).

### Form A before / after

The upstream "Process CSV → Analyze CSV…" example above keeps the *capability*
in the lead (upstream-faithful). The ai-skills overlay re-leads the **same
content** with the mandatory `Use this skill when …` phrase — capability
folded in, no information lost:

- Before (capability-lead, upstream-style): `description: Analyze CSV and
  tabular data files — compute summary statistics, add derived columns,
  generate charts, and clean messy data, even if the user does not say "CSV".`
- After (Form A, ai-skills overlay): `description: Use this skill when the
  user has a CSV, TSV, or Excel file and wants to explore, transform, or
  visualize it (even if they don't say "CSV" or "analysis") — to compute
  summary statistics, add derived columns, generate charts, and clean messy
  data.`

The "after" form begins with the exact token `Use this skill when ` and still
carries every keyword and the full capability from the "before" form.
