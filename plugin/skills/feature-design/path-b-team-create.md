# Path B Team-Create Prompt (feature-design)

The verbatim team-create natural-language prompt for Path B. Loaded from `SKILL.md` Step 1 when executing the Path B pipeline. Path B is `/feature-design`'s default — Path A is selected only when Agent Teams is unavailable or (rarely) when a regression has put every writing producer back into read-only mode.

## v0.3.8 design pattern — producers write their own files

As of plugin v0.3.8, nine producer roles in this workflow (`product-manager`, `marketing-strategist`, `system-architect`, `ui-ux-designer`, `db-engineer`, `security-engineer`, `qa-engineer`, `system-architect` reviewer, `product-manager` reviewer) ship with `Write` / `Edit` and an explicit "Write scope (docs/design artifacts only)" hard rule that forbids touching application code or infrastructure code. They write their assigned artefact directly — no fenced-block prose return, no Lead-writes-file restructure, no Bash-heredoc race.

The remaining intentionally read-only role is `eval-judge` (`tools: Read, Grep, Glob`). It returns a scored verdict in its final response; the Lead writes `REVIEW-LOG.md` from the judge's structured return.

Two clauses still need to be explicit in the team-create prompt:

1. **HTML-escape forbidance** — ASCII wireframes and code blocks containing `<`, `>`, `&` must appear as literal text in the written file, not as `&lt;`, `&gt;`, `&amp;`. Transmission-layer encoding occasionally HTML-escapes content; explicit instruction counters this.
2. **Eval-judge verdict-in-response** — judge returns scored verdict + per-dimension scores + cited findings in a fenced JSON block; the Lead writes `REVIEW-LOG.md`.

## Verbatim team-create prompt

Paste this into the natural-language team-create call. Substitute `<feature-slug>` with the kebab-case slug derived from the feature idea. Substitute `<feature-id>` with the same slug — files are written under `docs/features/<feature-id>/`.

```text
Create an agent team named "<feature-slug>-design-team" with these teammates, each using subagent definitions from the ai-assets plugin:

Wave 1 (parallel drafts — each teammate writes its own file):
- "pm" (ai-assets:product-manager) — writes docs/features/<feature-id>/PRD.md directly using its Write tool
- "marketing" (ai-assets:marketing-strategist) — writes docs/features/<feature-id>/MARKET-ANALYSIS.md directly (skip if not public-facing)
- "sysarch" (ai-assets:system-architect) — writes docs/features/<feature-id>/ARCHITECTURE.md directly

Wave 2 (parallel domain work — each teammate writes its own file or section):
- "ux" (ai-assets:ui-ux-designer) — writes docs/features/<feature-id>/UX-FLOW.md directly
- "db" (ai-assets:db-engineer) — writes docs/features/<feature-id>/DATA-MODEL.md directly
- "sec" (ai-assets:security-engineer) — writes its findings into docs/features/<feature-id>/RISKS.md directly (creates the file if missing; sec owns the "Security findings" section)
- "qa-design" (ai-assets:qa-engineer) — writes its acceptance-criteria section into docs/features/<feature-id>/RISKS.md directly (qa-design owns the "Test plan + acceptance criteria" section, appending to whatever sec wrote)

Wave 3 (sequential cross-check):
- "pm-review" (ai-assets:product-manager) — fresh PM-reviewer reading all wave-1 + wave-2 outputs, writes docs/features/<feature-id>/feedback.md directly
- "sysarch-review" (ai-assets:system-architect) — fresh architecture-reviewer reading all wave-1 + wave-2 outputs, writes docs/features/<feature-id>/architecture-review.md directly
- "judge" (ai-assets:eval-judge) — INTENTIONALLY read-only; scores the design pack against feature-design.md rubric; returns the full verdict + per-dimension scores + cited findings in a single fenced JSON block in its final message. The Lead writes REVIEW-LOG.md from the structured return — judge has no Write tool by design.

Use teammate-mode `in-process` by default (works in any terminal including Windows without WSL — no tmux/iTerm2 required). Pick `tmux` split-pane mode only if the user has explicitly indicated tmux or iTerm2 is available and they prefer it. If unsure, `in-process` is the safe choice.

Mandatory clauses for every teammate (include verbatim):

1. "Write your assigned artefact directly using your Write tool. The path is specified in the teammate brief above. Do NOT return prose to the Lead instead of writing — the Lead will not write your file for you (except for the judge, which is read-only by design)."

2. "ASCII wireframes, code blocks, and any `<` `>` `&` characters must appear as literal text in the file content — do NOT HTML-escape them to `&lt;`, `&gt;`, `&amp;`. Transmission-layer encoding occasionally converts these; counter it by writing the file directly with your Write tool rather than echoing content through Bash."

3. "Write scope is restricted to docs/design artifacts under docs/features/<feature-id>/ (plus the repo-root ARCHITECTURE.md for sysarch's optional system-level update). NEVER modify application source code, infrastructure code (Terraform, Helm, Dockerfiles, K8s manifests), CI workflows, or migration scripts — your agent definition's Hard Rules already forbid this."

4. "Wave-2 and Wave-3 teammates: before claiming your task, list the wave-1 (or wave-1+2) artefact paths you will Read so the Lead can verify your context window. Do not re-Read files that you have already Read this session."

5. "Eval-judge teammate only: return the scored verdict in a single fenced JSON block in your final message with fields { verdict: 'PASS'|'FAIL', overall_score: number, dimensions: { ... }, findings: [...] }. Do NOT attempt to write REVIEW-LOG.md — you have no Write tool. The Lead writes the log file from your structured return."

6. "Wave-3 reviewers (pm-review, sysarch-review): each writes to its OWN file — pm-review to docs/features/<feature-id>/feedback.md and sysarch-review to docs/features/<feature-id>/architecture-review.md. NEVER append to a shared REVIEW-LOG.md from a reviewer teammate — REVIEW-LOG.md is owned by the Lead and written ONCE after the judge returns, collating both reviewer files plus the judge's structured verdict. Concurrent reviewer appends to one file have no runtime locking and have caused field-observed lost writes."
```

## Concurrent-write avoidance (v0.3.10)

Path B has no file-locking primitive — two teammates writing to the same path concurrently is a last-writer-wins race. The v0.3.10 design pattern avoids this by giving every Wave-3 reviewer its own file:

- `pm-review` → `feedback.md`
- `sysarch-review` → `architecture-review.md`
- `judge` → no file (verdict-in-response)
- Lead (after judge returns) → `REVIEW-LOG.md` (collates the three above into one chronological log)

The Wave-2 split between `sec` and `qa-design` on `RISKS.md` is the one legitimate shared-file case, and it is serialised structurally: `qa-design` `dependsOn: [<sec-task-id>]` so it claims only after `sec` completes its append. Do NOT extend the shared-file pattern to Wave-3 reviewers — they have no `dependsOn` chain between them by design (parallel cross-checks).

## Agent roster — capability summary

For quick reference (full table with effort + model lives in `SKILL.md` Agent roster):

| Teammate | Tools (effective at spawn) | Writes file? | Prompt clause needed |
|---|---|---|---|
| `pm`, `marketing`, `ux`, `sysarch`, `db`, `sec`, `qa-design`, `pm-review`, `sysarch-review` | Read, Grep, Glob, [Bash], Write, Edit | YES — teammate writes directly | HTML-escape forbidance + Write-scope reminder |
| `judge` | Read, Grep, Glob | NO — verdict in response | Fenced JSON return; Lead writes `REVIEW-LOG.md` |

## When this prompt fails

If team-create returns "Agent Teams not enabled" — fall back to Path A per `wave-protocol.md`.

If the pre-spawn tool-capability check shows a writing-role regression in `plugin/agents/<name>.md` (a producer has lost `Write`/`Edit` since v0.3.8), prefer (a) fixing the agent definition over (b) restructuring the workflow. The Write-scope hard rule in each producer's body keeps the blast radius docs-only.

**TeamCreate success ≠ auto-claim enabled (v0.3.9).** `TeamCreate` can return success while the runtime's task auto-claim mechanism is disabled — typically when `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` is unset on the host or the runtime equivalent is off. Symptom: the team is created and visible in the panel, but no teammate self-claims any task. The Lead MUST NOT assume "team-create returned without error" implies "the pipeline is live". Apply the **90 s no-claim fast-fail rule (alpha.33-fast-fail)** — if NO teammate produces any activity (no transcripts, no file reads, no task transitions) within 90 seconds of team-create plus the initial `TaskCreate` round, this is alpha.33-fast-fail. The Lead surfaces the whole-team escalation prompt from `@team-protocols/lead-protocol.md` "Liveness watchdog" → "Team-wide silent idle" instead of running individual-role nudge cycles. A user-approved option 4 ("Path A for the remainder of the workflow") is the documented escape valve.

If team-create succeeds AND at least one teammate engaged but another goes idle after claiming a task, run the regular `lead-protocol.md` "Path B Liveness — Explicit Hand-off + Watchdog" procedure (90s × 2 nudges per silent role, then per-role escalation). With v0.3.8 producer capabilities the silent-idle should now be a rare alpha.31 flake (transcript-bus issue), not an alpha.32 tool-mismatch — the producer has Write, so silent-idle is real flake, not "physically cannot fulfil the task".
