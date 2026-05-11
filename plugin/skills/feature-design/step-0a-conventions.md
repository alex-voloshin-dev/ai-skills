# Step 0a — Repo-local conventions + partial-pack mode

Mandatory pre-pipeline check executed by `feature-design-lead` before announcing Path B / Path A. The default skill output layout (`docs/features/<id>/{PRD,ARCHITECTURE,UX-FLOW,DATA-MODEL,RISKS,IMPLEMENTATION-PLAN,REVIEW-LOG}.md`) does NOT match every target repo. Without this check, the Lead writes to the wrong path and either duplicates pre-existing design docs or contradicts the repo's documented convention.

## What the Lead does in Step 0a

1. **Detect repo-local conventions.** Read these candidates if present (first hit wins):
   - `features/CLAUDE.md`
   - `features/AGENTS.md`
   - `docs/CLAUDE.md`
   - `docs/features/CLAUDE.md`
   - `<repo-root>/CLAUDE.md` "Feature docs" section if present

   Look for: target directory pattern (`features/planned/<id>/` vs `docs/features/<id>/`), required filename set (e.g. `prd.md + design.md + acceptance-criteria.md + user-stories.md`), consolidation rules (single `design.md` vs separate `ARCHITECTURE/UX-FLOW/DATA-MODEL/RISKS`), kebab-case vs snake_case ID convention.

2. **Detect partial-pack state.** Glob both default and convention-detected paths for any pre-existing PRD-like doc:
   - `features/**/<id>/{prd,PRD}.md`
   - `docs/features/**/<id>/{prd,PRD}.md`
   - `features/**/<id-similar>/*` (fuzzy match on slug — different word order, plural/singular)

3. **Pick mode** based on the detected state:

   | Detected state | Mode | What changes |
   |---|---|---|
   | No PRD anywhere | `standard` | Full pipeline writes all artefacts under the convention path |
   | PRD exists, no design / AC / data-model | `partial-pack` | Skip Wave 1 PM (PRD is input, not deliverable); Wave 1 sysarch + marketing run as usual; Wave 2 fills the gaps next to the existing PRD; judge optional (PRD already vetted) |
   | Full pack exists (PRD + design + AC + data-model) | `route-to-develop` | This is not a `/feature-design` job; advise the user to run `/develop` instead |
   | PRD exists, partial conflicts with repo convention | `partial-pack-realign` | partial-pack, but the first Lead action is to `mv` the existing PRD to the convention path; record the rename in `REVIEW-LOG.md` Step-0 notes |

4. **Consolidate-or-split decision.** If the repo convention requires a single `design.md` instead of `ARCHITECTURE.md + UX-FLOW.md + DATA-MODEL.md + RISKS.md`, the Lead overrides the default file plan:
   - Each Wave-2 producer (sysarch, ux, db, sec, qa) is instructed in its spawn prompt to write its section into `design.md` under a labelled `## <Section>` header rather than its own file.
   - The Wave-2 producers coordinate via the shared task list — db writes after sysarch; sec + qa write after ux. Use `dependsOn` on the same target file to serialise writers per `g7-contracts.md` "Only ONE agent may edit files at any time" rule.
   - The final `design.md` structure must match the order the repo convention specifies (typically: `## Overview → ## Architecture → ## UX Flow → ## Data Model → ## Risks → ## Acceptance Criteria`).

5. **Judge optional in partial-pack mode.** If the PRD was vetted before this session (`/feature-design` runs to add the design pack only), eval-judge becomes optional — run it ONLY if the user explicitly requests scoring, or if the spawn prompts produced unusually divergent outputs. Record the skip-or-run decision in `REVIEW-LOG.md` Step-0 notes with the reason.

## Announce the chosen mode

After Step 0a, the Lead announces (one line, before any spawn):

```text
[lead] Step 0a: repo conventions detected (<path-pattern>, files=<file-list>). Mode: <standard | partial-pack | partial-pack-realign | consolidated | route-to-develop>. Input PRD: <path | none>. Judge: <required | optional | skipped>.
```

## When this step finds nothing

If no repo-local conventions are present (no `features/CLAUDE.md`, no `docs/CLAUDE.md`, no PRD anywhere), proceed with the default `docs/features/<feature-id>/` layout and the full Wave 1 / 2 / 3 pipeline. Record `Mode: standard (no repo conventions detected)` in the announcement.

## Why this step exists

Field feedback from the f4ai session: the skill defaulted to `docs/features/<id>/{PRD,ARCHITECTURE,UX-FLOW,DATA-MODEL,RISKS}.md` but the target repo's `features/CLAUDE.md` required `features/planned/<id>/{prd,design,acceptance-criteria,user-stories}.md`. The model manually consolidated four agents' outputs into a single `design.md`, ignored Wave 1 PM (PRD already existed), and changed the target path mid-flight — none of which the skill described. Step 0a formalises that improvisation.
