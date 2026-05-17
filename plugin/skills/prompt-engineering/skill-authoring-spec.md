# Skill Authoring Spec & Best Practices

Faithful digest of the agentskills.io skill-authoring guidance — the cached
source of truth for `/plugin-author create`/`audit` and the `prompt-engineer`
agent when DEV-ing/reviewing a plugin skill. Re-fetch the live pages when
network is available; otherwise these cached rules apply. Sources:
https://agentskills.io/specification · /skill-creation/best-practices ·
/skill-creation/using-scripts · /skill-creation/evaluating-skills.
Description optimization (the triggering surface) is digested separately in
`optimizing-descriptions.md` (same dir).

---

## 1. Specification

### Directory structure

```
skill-name/
├── SKILL.md          # Required: metadata + instructions
├── scripts/          # Optional: executable code
├── references/       # Optional: documentation
├── assets/           # Optional: templates, resources
└── ...               # Any additional files or directories
```

### Frontmatter fields

| Field | Required | Constraints |
|---|---|---|
| `name` | Yes | Max 64 chars. Lowercase letters, numbers, hyphens only. Must not start/end with a hyphen. |
| `description` | Yes | Max 1024 chars. Non-empty. What the skill does AND when to use it. |
| `license` | No | License name or reference to a bundled license file. Keep short. |
| `compatibility` | No | Max 500 chars. Environment requirements (intended product, system packages, network access). Most skills do NOT need it. |
| `metadata` | No | Arbitrary string→string key-value map. Use reasonably-unique keys to avoid conflicts. |
| `allowed-tools` | No | Space-separated string of pre-approved tools. **Experimental** — support varies by client. |

`name` detailed rules: 1–64 characters; unicode lowercase alphanumeric
(`a-z`) and hyphens (`-`) only; must NOT start or end with a hyphen; must NOT
contain consecutive hyphens (`--`); **must match the parent directory name**.

`description`: 1–1024 characters; describe both what the skill does and when
to use it; include keywords that help agents identify relevant tasks. Full
triggering guidance: `optimizing-descriptions.md`.

`compatibility` examples: "Designed for Claude Code (or similar products)" /
"Requires git, docker, jq, and access to the internet" / "Requires Python
3.14+ and uv". 1–500 chars if provided. `metadata` example: `author:
example-org`, `version: "1.0"`. `allowed-tools` example: `Bash(git:*)
Bash(jq:*) Read`.

### Body content

Markdown after frontmatter, no format restrictions. Recommended sections:
step-by-step instructions; input/output examples; common edge cases. The
agent loads the entire file on activation — split longer content into
referenced files.

### Optional directories

- `scripts/` — executable code agents can run. Self-contained or clearly
  document dependencies; helpful error messages; handle edge cases.
- `references/` — on-demand docs; keep each file focused/small.
- `assets/` — static resources: templates, images, data files.

### Progressive disclosure (3 levels)

1. **Metadata** (~100 tokens): `name` + `description` loaded at startup for all
   skills.
2. **Instructions** (< 5000 tokens recommended): full `SKILL.md` body loaded on
   activation.
3. **Resources** (as needed): files in `scripts/`/`references/`/`assets/`
   loaded only when required.

Keep main `SKILL.md` under **500 lines**. Move detailed reference material to
separate files.

### File references

Relative paths from the skill root. Keep references **one level deep** from
`SKILL.md` — avoid deeply nested reference chains.

### Validation

`skills-ref validate ./my-skill` (github.com/agentskills/agentskills) — checks
frontmatter validity + naming conventions.

---

## 2. Best practices

### Start from real expertise

Don't generate a skill from generic LLM training knowledge → vague generic
procedures. Ground in real expertise:
- **Extract from a hands-on task** — complete a real task with the agent, then
  extract the reusable pattern (steps that worked; corrections you made;
  input/output formats; context you provided).
- **Synthesize from project artifacts** — internal docs/runbooks/style guides;
  API specs/schemas/configs; code-review comments & issue trackers; VCS
  history; real failure cases + resolutions. Project-specific, not generic.

### Refine with real execution

First draft needs refinement. Run against real tasks; feed ALL results back
(not just failures): what triggered false positives? what was missed? what
could be cut? Read execution **traces**, not just final outputs — wasted
steps ⇒ vague instructions / inapplicable instructions the agent follows
anyway / too many options without a clear default.

### Spending context wisely

- **Add what the agent lacks, omit what it knows** — don't explain what a
  PDF/HTTP/migration is. Ask "Would the agent get this wrong without this
  instruction?" If no, cut it.
- **Design coherent units** — like deciding what a function does. Too narrow ⇒
  many skills load per task (overhead, conflicts). Too broad ⇒ hard to activate
  precisely.
- **Aim for moderate detail** — concise stepwise guidance + a working example
  beats exhaustive docs. Over-comprehensive skills hurt.
- **Structure large skills with progressive disclosure** — < 500 lines & 5000
  tokens; move detail to `references/`. Tell the agent *when* to load each
  file ("Read `references/api-errors.md` if the API returns a non-200
  status"), not a generic "see references/".

### Calibrating control

- **Match specificity to fragility.** Freedom when multiple approaches are
  valid & the task tolerant (explain *why*, not rigid directives).
  Prescriptive when fragile/consistency-critical/sequence-bound ("Run exactly
  this sequence … Do not modify the command"). Most skills mix — calibrate
  each part.
- **Provide defaults, not menus** — pick a default, mention alternatives
  briefly. Not "use pypdf, pdfplumber, PyMuPDF, or pdf2image".
- **Favor procedures over declarations** — teach how to approach a class of
  problems, not what to produce for one instance. Specific details (output
  templates, "never output PII", tool-specific instructions) still allowed; the
  *approach* must generalize.

### Patterns for effective instructions

- **Gotchas sections** — highest-value content: concrete environment-specific
  corrections to mistakes the agent will make (soft deletes / id-name
  mismatches / /health vs /ready). Keep in `SKILL.md`; when you correct an
  agent mistake, add it to gotchas.
- **Templates for output format** — concrete template; short inline, long →
  `assets/`. **Checklists** for multi-step workflows.
- **Validation loops** — do work → run validator → fix → repeat until passes
  (a reference doc can be the validator).
- **Plan-validate-execute** — for batch/destructive ops: create an
  intermediate plan in a structured format, validate against the source of
  truth, then execute; the validation script's errors must be specific enough
  to self-correct.
- **Bundling reusable scripts** — if traces show the agent reinventing the
  same logic each run, write a tested script once and bundle in `scripts/`.

---

## 3. Using scripts in skills

### One-off commands

When an existing package does the job, reference it directly in SKILL.md
without `scripts/`. Dep-resolving runners: `uvx` (Python, needs uv), `pipx
run`, `npx`, `bunx`, `deno run` (needs `--allow-*`), `go run`. Tips: **pin
versions** (`npx eslint@9.0.0`); **state prerequisites** in SKILL.md or use
the `compatibility` frontmatter field; **move complex commands into scripts**
when hard to get right first try.

### Referencing scripts

Use relative paths from skill root. List available scripts ("## Available
scripts", one line each), then instruct the agent to run them. Execution
paths are relative to the skill directory root.

### Self-contained scripts (inline deps)

- **Python — PEP 723**: TOML block in `# /// script` … `# ///`; run with `uv
  run`. pipx also supports it. Pin with PEP 508 (`"beautifulsoup4>=4.12,<5"`);
  `requires-python`; `uv lock --script` for reproducibility.
- **Deno**: `npm:`/`jsr:` specifiers; semver `@1.0.0`/`@^1.0.0`; globally
  cached. **Bun**: auto-installs at runtime; pin `cheerio@1.0.0`; disabled if
  a node_modules exists up-tree. **Ruby**: `bundler/inline` `gemfile do …
  end`; pin explicitly; existing Gemfile/BUNDLE_GEMFILE can interfere.

### Designing scripts for agentic use

- **Avoid interactive prompts** — HARD requirement; agents run non-interactive
  shells; a TTY-blocking script hangs indefinitely. Accept input via
  flags/env/stdin; clear error+usage when required input is missing.
- **Document usage with `--help`** — the primary way an agent learns the
  interface; keep concise (it enters context).
- **Helpful error messages** — what went wrong, what was expected, what to try.
- **Structured output** — prefer JSON/CSV/TSV; data → stdout,
  progress/warnings → stderr.
- **Further**: idempotency; input constraints (enums/closed sets, reject
  ambiguous input); `--dry-run` for destructive/stateful ops; documented exit
  codes per failure type; safe defaults (`--confirm`/`--force`); **predictable
  output size** (harnesses truncate ~10–30K chars — default to summary/limit,
  support `--offset`, or require `--output FILE|-`).

---

## 4. Evaluating skill output quality

- Test case = prompt + expected output (human-readable) + optional input
  files. Store in `evals/evals.json` inside the skill dir. Start with 2–3
  cases; vary prompts (casual/precise); cover edge cases
  (boundary/malformed/ambiguous); realistic context (paths, column names).
- Run each case **with skill** and **without skill** (or vs previous version)
  for a baseline. Workspace `<skill>-workspace/iteration-N/<eval>/`
  `{with_skill,without_skill}/{outputs,timing.json,grading.json}` +
  `benchmark.json`. Hand-author only `evals/evals.json`. Each run starts with
  a **clean context** (subagents give this naturally). When improving an
  existing skill, snapshot the previous version as baseline (`old_skill/`).
  Capture timing (`{total_tokens, duration_ms}`).
- **Assertions** added AFTER first outputs: verifiable statements (valid JSON /
  labeled axes / ≥3 recommendations). Avoid "is good" and exact-phrase
  brittleness — style/feel → human review. **Grading**: PASS/FAIL with
  concrete evidence quoting the output; code-checkable assertions →
  verification script. **Blind comparison** for two versions: present both
  outputs to an LLM judge without revealing source.
- **Aggregate** to `benchmark.json` with with/without/delta (pass_rate, time,
  tokens) — delta = what the skill costs vs buys. **Analyze**: drop assertions
  always-pass-both; investigate always-fail-both; study pass-with/fail-without
  (where the skill adds value); tighten high-stddev (flaky) instructions.
- **Iterate loop**: failed assertions + human feedback + transcripts + current
  SKILL.md → LLM proposes changes → apply → rerun iteration N+1 → grade →
  review → repeat. Stop when satisfied / no improvement. `skill-creator`
  automates much of this.

---

## ai-skills overlay (additive, never weaker than upstream)

- Body **≤ 12000 characters** for `SKILL.md`/rule files (stricter
  operationalization of the upstream ≤500-line / ≤5000-token guidance)
- **English-only**; **no absolute user-machine paths**; references **one level
  deep** from `SKILL.md` (matches upstream)
- Description in **third person** + the **`Use when …`** trigger pattern (H5)
  — see `optimizing-descriptions.md`
- User-invocable forked workflows: `context: fork` + `argument-hint`;
  knowledge-only: `disable-model-invocation: true`
- Any add/hide of a skill/agent/rubric/sample bumps `EXPECTED_COUNTS` in
  `plugin/dev/validate.py` same change set (adding a *resource file* to an
  existing skill does NOT change skill count)
