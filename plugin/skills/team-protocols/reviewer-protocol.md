# Reviewer Protocol

Rules for the Reviewer agent in a multi-agent team. The Reviewer uses `subagent_type: "software-engineer"` with skill `code-review`.

## Independent Verification

CRITICAL: Do NOT trust the Developer's report alone. Independently verify:

- Read the actual changed files on disk to confirm edits are present
- If files were supposed to be deleted — check they are actually gone
- If new files were created — check they actually exist with correct content
- If old code was supposed to be replaced — check the old code is not still present alongside the new
- Watch for the **"ghost changes" pattern**: agent reports a change but the file on disk is unchanged

If changes did not actually persist — flag this immediately as a **HIGH severity blocker**.

## Issue Reporting (G7 return contract)

Reviewer return MUST conform to `plugin/schemas/return-contract.schema.json`. If issues found, populate `result.summary` with the list of findings (file path + line + severity + fix instruction per finding) and use `status: partial`. If no issues, use `status: ok` with `result.summary: "Approved — no issues found"`.

For each finding inside `result.summary`:

- File path and line reference
- Severity (high / medium / low)
- Clear explanation of the problem and what to fix

## Approval

If there are no issues — return `status: ok`, `result.summary: "Task approved, proceed to the next task"` (or `"Fix approved"` for bugfix workflows).

## Boundaries

- Do NOT write code — only review
- Read-only access to all files
- If the workflow includes acceptance criteria or a bug report — check the fix against those requirements
- Reviewer agent's `tools` field MUST exclude `Write` and `Edit` (enforced via `disallowedTools` in agent frontmatter)

## Findings envelope (file-channel, v0.3.11)

In addition to the canonical G7 return via the bus, write your verdict envelope to disk as a defensive backstop. The Lead's `team-gate-reconciliation` hook + `Monitor` will pick it up even if `SendMessage` / `TaskUpdate` augmentation is intermittent on your tool surface (alpha.31 / alpha.35 / alpha.36):

```bash
mkdir -p .ai-skills-memory/sessions/<sid>/team-envelopes
cat > .ai-skills-memory/sessions/<sid>/team-envelopes/findings-reviewer-WP-N.json.tmp <<'JSON'
{
  "trace_id": "<spawn-trace_id>",
  "verdict": "approved" | "changes_requested",
  "files_changed": [],
  "summary": "<one line>",
  "findings": [
    {"file": "<path>", "line": <n>, "severity": "high|medium|low", "issue": "<what>", "fix": "<how>"}
  ],
  "next_actions": []
}
JSON
mv .ai-skills-memory/sessions/<sid>/team-envelopes/findings-reviewer-WP-N.json.tmp \
   .ai-skills-memory/sessions/<sid>/team-envelopes/findings-reviewer-WP-N.json
```

The `.tmp` → `mv` pattern is required so the Lead's `Monitor` never reads partial JSON. The `<sid>` is from the spawn payload's `state_slice.session_id`.

This is in addition to, NOT instead of, the canonical G7 return via the bus. Both channels carry the same verdict. The file-channel is the liveness backstop.

You remain read-only (`Read`, `Grep`, `Glob`, `Bash` for the `mv` only — no `Write` / `Edit` on source files). Writing the envelope file via `Bash` heredoc + `mv` is the only file-write operation permitted to the Reviewer, and it touches only `.ai-skills-memory/sessions/<sid>/team-envelopes/` — never source code, never docs, never tests.

## Findings delivery fallback (alpha.35)

If you have completed your review but your `TaskUpdate` or `SendMessage` tools are unavailable in the current Path B session (the team-runtime augmentation did not attach to your tool surface — a known alpha flake), do NOT silently idle and do NOT ask the Lead to "grant you those tools" or "give you TaskList access" — that would break read-only role isolation. Instead, deliver your verdict in your next conversation turn so the Lead can write the G7 envelope on your behalf (same pattern as `eval-judge`). Include:

- `verdict:` — `approved` or `changes_requested`
- `files_changed:` — always `[]` for the Reviewer
- `summary:` — one line
- `findings:` — per finding: file path + line, severity (high / medium / low), what is wrong and how to fix
- `next_actions:` — concrete follow-up steps for the Developer (or empty list for `approved`)

The Lead is monitoring your transcript and will pick up the reply, write the G7-equivalent envelope into `REVIEW-LOG.md`, and close your task with your verdict. This is the documented recovery for alpha.35 — see `path-selection-rules.md` Observed failure modes and `lead-protocol.md` Path B Liveness 4d.
