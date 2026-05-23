# /knowledge-sync — KB-Hygiene Enforcement (CONVENTIONS.md conformance gate · WP-3b)

The pre-write conformance gate that makes `knowledge/CONVENTIONS.md` a hard
contract on every generated/updated doc. `SKILL.md` carries the binding Hard Rule
and the numbered pipeline step; this file is the executable detail. It runs
**per area, on the content-writer's output, AFTER reconciliation and IN THE SAME
pre-write gate band as the C3 secret-scan / C3b output-validation / C4 path-deny
gates, BEFORE the update-policy write** (SKILL.md step 7). Security depth lives in
`security.md`; fan-out/policy/baseline in `execution.md`.

> This is a **quality gate**, complementary to the security gate (G1 wrapping +
> propose-only). It is also scored by eval dimension **D7 — Conventions
> adherence** (a release blocker; see the design pack QA section).

---

## 1. What it reads — `CONVENTIONS.md` + the config `conventions:` block

The gate validates each doc against `knowledge/CONVENTIONS.md` (the human-readable
contract) interpreted through the machine-readable `conventions:` block in
`knowledge/.knowledge-sync.yml`. The config fields it reads (all present in
`knowledge-sync-config-template.yml`):

| Config field | Default | Drives |
|---|---|---|
| `conventions.enforcement` | `strict` | `strict` blocks non-conforming writes; `advisory` warns only |
| `conventions.file` | `knowledge/CONVENTIONS.md` | the authoritative style guide read each run |
| `conventions.sizing.hard_cap_words` | `3000` | over-cap → split (non-overridable floor) |
| `conventions.sizing.soft_cap_words` | `2000` | over-soft-cap → flag "consider splitting" in PR |
| `conventions.sizing.target_words` | `1500` | read-verbatim target (informational) |
| `conventions.sizing.split_strategy` | `by-h2-topic` | how an over-cap doc is split |
| `conventions.structure.one_topic_per_doc` | `true` | one-topic check |
| `conventions.structure.diataxis_mode_per_doc` | `true` | one-mode check (tutorial\|how-to\|reference\|explanation) |
| `conventions.structure.max_h2_sections` | `9` | > max H2 → split signal |
| `conventions.structure.toc_over_words` | `1200` | add a ToC above this length |
| `conventions.front_matter.required` | `[title, area, owner, last_reviewed, source_refs]` | required-key validation (see §2 floor) |
| `conventions.naming.pattern` | `kebab-case` | filename pattern check |
| `conventions.naming.one_h1_per_doc` | `true` | single-H1 check |

If `conventions:` is absent from an older config, fall back to the floor (§2) plus
the `CONVENTIONS.default.md` defaults, and note the fallback in the L4 record.

---

## 2. Front-matter required list vs the non-overridable floor (Decision #14)

This resolves the WP-1 review carry-forward (floor vs `required`). The two are
**distinct** and must not be conflated:

- **Effective required list** = `config.conventions.front_matter.required`. The
  gate validates each doc's front-matter against *this* list. The shipped default
  is the **5-key** `[title, area, owner, last_reviewed, source_refs]` — it ADDS
  `owner` on top of the floor.
- **Non-overridable floor** = the **4 keys** `title, area, last_reviewed,
  source_refs`. A repo config MAY add to `required` (as the default does with
  `owner`) or otherwise tighten; it MAY NOT remove a floor key.

**Config validation (runs once, before the per-doc loop):** compute
`missing_floor = {title, area, last_reviewed, source_refs} − set(required)`. If
`missing_floor` is non-empty, the config has dropped a floor key — **repair** it
by re-adding the missing floor key(s) to the effective required list used for this
run (deterministic), log a `config_repaired` note to the L4 record at WARN, and
proceed with the floor-restored list. (The floor cannot be removed; a config that
tries is treated as if it never dropped it.) `owner` is NOT a floor key, so a repo
that wants only the 4-key minimum may legitimately drop `owner` from `required` —
that is allowed and is NOT repaired.

This keeps the gate consistent with `CONVENTIONS.default.md` (which states the
4-key floor under "Required front-matter" / "The non-overridable floor" while the
front-matter example and the config template keep the 5-key default) — they do not
contradict: the **default** is 5 keys, the **floor** is 4.

The hard-cap (`3000` words) and `update_policy.default: propose` are the other two
non-overridable floor items (Decision #11/#14) — enforced by this gate (cap) and
by C2 (propose) respectively.

---

## 3. The per-doc checks

For each file a writer produced/updated in the area (before any Write/Edit lands):

| # | Check | Class | Source of truth |
|---|---|---|---|
| H1 | front-matter present + every key in the effective `required` list present and non-empty; values well-formed (`last_reviewed` is a date; `source_refs` is a non-empty list) | deterministic | `front_matter.required` (floor-restored, §2) |
| H2 | word count ≤ `sizing.hard_cap_words` | deterministic (over-cap → split) | `sizing.hard_cap_words` |
| H3 | word count ≤ `sizing.soft_cap_words` | advisory flag (never blocks) | `sizing.soft_cap_words` |
| H4 | exactly one H1 (`# `) line, matching the front-matter `title` | deterministic | `naming.one_h1_per_doc` |
| H5 | filename matches `naming.pattern` (kebab-case `[a-z0-9]+(-[a-z0-9]+)*\.md`) | deterministic | `naming.pattern` |
| H6 | ≤ `structure.max_h2_sections` H2 sections | deterministic (over → split signal) | `structure.max_h2_sections` |
| H7 | a ToC is present when word count > `structure.toc_over_words` | deterministic | `structure.toc_over_words` |
| H8 | one topic per doc (no "and"-joined scope; sections cohere) | **non-deterministic** | `structure.one_topic_per_doc` |
| H9 | one Diátaxis mode per doc (not mixed tutorial/how-to/reference/explanation) | **non-deterministic** | `structure.diataxis_mode_per_doc` |
| H10 | no internal contradiction with itself or a canonical doc it overlaps | **non-deterministic** | `CONVENTIONS.md` accuracy rules |

Word count = whitespace-delimited tokens in the body **excluding** the YAML
front-matter block and fenced code blocks (code is not prose; counting it would
force spurious splits of reference docs).

---

## 4. Deterministic vs non-deterministic — outcomes

**Deterministic violations** (H1, H2, H4, H5, H6, H7) → **auto-fix or split** in
place, then re-run the check on the corrected output:

- **Missing/empty front-matter key** → insert the key. For `title` use the H1
  text; `area` from the area being processed; `last_reviewed` = today; `source_refs`
  = the matched changed-file set for this area; `owner` (if required and absent) →
  carry from a sibling doc in the area, else insert the placeholder
  `<TODO: owner>` and flag for human (do not invent an owner).
- **Wrong filename case** → rename to kebab-case (and update referrers in the same
  area in the same change — stable-anchor rule).
- **Multiple H1** → keep the first, demote the rest to H2 (or split, if they are
  clearly separate topics — defer to the split path).
- **Over hard cap / > max H2** → **split** per `sizing.split_strategy` (default
  `by-h2-topic`: each H2 section becomes its own kebab-named doc with valid
  front-matter; emit a short index doc that links them). Each split child is
  re-validated by this gate before it is allowed to the write band.
- **Missing ToC over `toc_over_words`** → generate a ToC from the H2 headings.

**Non-deterministic violations** (H8, H9, H10 — mixed topics, mixed Diátaxis mode,
contradiction) → **the area FAILS**. These cannot be safely auto-corrected by a
deterministic transform; an automated "fix" would risk silently rewriting meaning.
The area is marked `failed`, NOTHING for that area is written, its baseline is NOT
advanced (R08), and the violation is **flagged in the draft PR body** (and the L4
`run.json` `conventions` block) for a human to resolve.

**Soft-cap (H3)** is never a block: over the soft cap but under the hard cap →
add a `consider splitting` flag to the PR body; the doc is still written.

---

## 5. Enforcement modes — `strict` (default) vs `advisory`

`conventions.enforcement` selects the mode:

| Mode | Deterministic violation | Non-deterministic violation |
|---|---|---|
| **`strict`** (default) | auto-fixed/split, then written (a doc that still fails after the fix attempt is NOT written → the area fails) | **area fails; nothing written; flagged in PR**; baseline not advanced |
| **`advisory`** | applied if cheap; otherwise the doc is written as-is with a PR flag | the doc is written as-is; the violation is flagged in the PR; the area does NOT fail on conventions grounds |

Under `strict` the binding invariant is: **a non-conforming doc is NEVER written.**
A deterministic violation must be repaired (or split) and re-pass the check before
the write band; a non-deterministic one fails the area. `advisory` downgrades every
outcome to a warning and never blocks a write on conventions grounds (security
gates C3/C3b/C4 still block regardless of conventions mode).

---

## 6. Where it sits in the pipeline (gate band ordering)

The conformance gate runs **inside SKILL.md step 7**, after the writer returns are
reconciled and re-wrapped (G1), in the same pre-write band as the security gates,
**before** step 8 (update-policy write):

```
reconcile + re-wrap returns (G1)
        │
        ▼  pre-write gate band (per area, BEFORE any Write/Edit lands)
   ┌─────────────────────────────────────────────────────────────┐
   │ C3  secret-scan        (security.md)  — block on hit         │
   │ C3b output-validation  (security.md)  — block on hit         │
   │ C4  path deny + traversal (security.md) — block on hit       │
   │ H   KB-hygiene conformance (this file) — strict: block/split │
   └─────────────────────────────────────────────────────────────┘
        │ all gates pass (or deterministic fixes applied + re-passed)
        ▼
   apply update_policy (step 8) → propose (PR) | direct
```

Ordering rationale: the **security gates run first** — never spend hygiene effort
(splitting, front-matter repair) on content that a secret-scan or path-deny is
about to reject anyway, and never let a hygiene auto-fix reshape content in a way
that could slip past a security gate that already ran. A security block aborts the
area before the hygiene gate is reached. If the hygiene gate auto-fixes/splits a
doc, the security gates (C3/C3b/C4) re-run on each resulting child before it is
written (a split can introduce new files / new paths).

A hygiene failure (strict, non-deterministic) uses the **same abort semantics** as
C3/C3b/C4: abort that area, do NOT advance its baseline, record the reason. It is
recorded under a `conventions` key in the L4 record rather than `blocked_ops`
(which stays reserved for security blocks), at severity WARN for a flagged area
(human follow-up expected) — distinct from the ERROR severity a security block
carries.

---

## 7. L4 record additions

Extend the area entries in `run.json` (`execution.md` §5) with a `conventions`
block per area, e.g.:

```json
{
  "area": "tech-docs",
  "policy": "propose",
  "status": "failed",
  "conventions": {
    "mode": "strict",
    "deterministic_fixes": ["added front-matter: source_refs", "renamed Api_Ref.md -> api-ref.md"],
    "splits": ["split overview.md by-h2-topic into 3 docs + index"],
    "soft_cap_flags": ["concepts.md ~2300 words"],
    "failures": ["mixed Diátaxis mode (how-to + reference) in billing.md"],
    "config_repaired": []
  }
}
```

`config_repaired` records any floor key that was re-added to a config whose
`front_matter.required` had dropped it (§2). All `conventions.failures` entries are
mirrored into the draft PR body so the human reviewer sees exactly why an area was
held back. PII-filter every field before persistence (`memory-discipline.md`), as
with all L4 telemetry.

---

## 8. Self-check anchors

- The gate reads ONLY `conventions.*` fields that exist in
  `knowledge-sync-config-template.yml` (§1 table) — no invented fields.
- The floor is **4 keys** (`title, area, last_reviewed, source_refs`); the default
  `required` is **5 keys** (adds `owner`); `owner` is droppable, a floor key is not
  (§2). This matches `CONVENTIONS.default.md` and the config template — the default
  is 5, the floor is 4; they do not contradict.
- `strict` (default) never writes a non-conforming doc; `advisory` only warns.
- The gate runs in the SKILL.md step-7 pre-write band, after the C3/C3b/C4 security
  gates, before the step-8 write.
