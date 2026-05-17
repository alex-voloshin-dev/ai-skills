# ai-skills

> Vendor-agnostic agentic-dev tooling: 26 agents, 73 skills, and 45 eval
> rubrics that work across Claude Code, Codex, and Windsurf.

Engineering teams adopting AI coding agents hit the same wall: ad-hoc
patterns that work for one developer don't scale to the team, evaluation
is hand-wavy, and switching runtimes means rewriting everything. This
repo is the working playbook of patterns that survived production use
across all three major agentic-dev runtimes — with a tracked parity
matrix so you know exactly what's available where, and 45 eval rubrics
with 270 calibrated samples so "is it working?" has an answer.

---

## What's inside

| Asset | Count | What it is |
|-------|-------|------------|
| **Agents** | 26 | Specialized sub-agents (review, planning, testing, refactor, security, etc.) — invoked from a parent agent or a slash command |
| **Skills** | 53 | Reusable, named instruction packs that adapt the agent's behavior to a domain (Python, Go, AWS, frontend, etc.) |
| **Eval rubrics** | 45 | Scorable rubrics for AI coding-agent output — code quality, test discipline, prompt-following, etc. |
| **Calibration samples** | 270 | Labeled examples (6 per rubric) that show what each rubric catches in practice — not theory |
| **Hooks** | 18 | Pre/post-action interceptors for guardrails (no `git commit`, file size limits, etc.) |
| **Rules** | 12 | Cross-cutting policies enforced at the agent or repo level |
| **Workflows** | 32 | User-invocable slash commands that compose agents + skills into a multi-step recipe |

**Codex + Windsurf parity packages:** 39 shared skills, 22 roles, 8
rules. Cross-runtime parity is tracked in
[`review/parity-matrix.md`](./review/parity-matrix.md) — check there for
the per-runtime availability of any capability.

---

## Why this exists

### Tri-vendor parity, not vendor lock-in

Almost every public agentic-dev expert is locked to one runtime. This
repo tracks parity across all three with a public matrix. When a
feature lands in Claude Code first, the matrix tracks the gap and the
workaround for Codex / Windsurf until parity is reached.

### Eval-driven, not hand-wavy

Most public discourse on AI coding-agent evaluation is a vague "AI eval
is hard". The 45 rubrics ship with 270 calibrated samples showing what
each rubric actually catches in production code. If you're
operationalizing AI coding agents on a team, "how do I know it's
working?" has an answer.

### Formal-methods background applied to agentic dev

LTL, model checking, and FRR techniques apply to agent specifications
more directly than people think. The intersection between formal
methods and agentic dev is one of the least-explored angles in public
discourse, and a few patterns in this repo lean on that background.

---

## Quick start

**Prerequisites** — clone the repo:

```bash
git clone https://github.com/alex-voloshin-dev/ai-skills.git
cd ai-skills
```

### Claude Code

The plugin is not yet on a public marketplace. Install from the local
clone:

```bash
claude --plugin-dir ./plugin
```

All 32 user-invocable workflows appear under the `ai-skills:` namespace
in `/help`. To reload after editing plugin files in the same session:

```text
/reload-plugins
```

See [`plugin/README.md`](./plugin/README.md) for full plugin install and
usage, or [`plugin/docs/getting-started.md`](./plugin/docs/getting-started.md)
for a guided tour.

### Codex

The installer syncs the Codex package (`.codex/`) plus the shared
skills (`.agents/`) into your home directory:

```bash
bash install.sh
```

Idempotent — files removed from the repo are also removed from
`~/.codex/` / `~/.agents/` on re-run. Codex root instructions live in
[`AGENTS.md`](./AGENTS.md).

### Windsurf

Same installer — it also syncs the Windsurf package (`.windsurf/`)
into `~/.windsurf/`:

```bash
bash install.sh
```

On Windows use `install.ps1` instead. Windsurf-native hooks are wired
through [`.windsurf/hooks.json`](./.windsurf/hooks.json) — see
[`TESTING.md`](./TESTING.md) for hook validation.

A minimal first run — once installed, sample the eval harness in
dry-run mode (no API key needed) to see the rubric system at work:

```bash
$ python3 plugin/eval/runner.py --tier 2 --dry-run --sample-rubrics 3 --samples-per-rubric 2

=== Tier 2 — Judge-Calibration Drift Smoke ===
Sample seed: 42
Rubrics sampled: 3 (analyze, code-review, spike)
API available: False
Tokens used: 0 (soft 50000, hard 150000)

  [ERR ] analyze       good  tech-stack-comparison.score-4.0.md       -- dry-run
  [ERR ] analyze       bad   opinion-without-evidence.score-1.0.md    -- dry-run
  [ERR ] code-review   good  clean-pass.score-3.8.md                  -- dry-run
  [ERR ] code-review   bad   mixed-with-security-scan.score-1.4.md    -- dry-run
  [ERR ] spike         good  auth-openidconnect-vs-oauth.score-4.4.md -- dry-run
  [ERR ] spike         bad   unsubstantiated-claim.score-1.3.md       -- dry-run
```

Each rubric ships with paired "good" and "bad" calibration samples
labeled with target scores. That's how you tell whether the judge is
drifting before it shows up in production. Drop `--dry-run` (with an
API key in env) to run the full Tier 2 calibration smoke.

---

## Use cases

**Operationalizing AI coding agents on a team of 50+.** Stop writing
one-off prompt libraries that don't survive turnover. The agents and
skills here are designed to be installed as a unit, with eval rubrics
to verify they're actually working in your codebase.

**Picking an agentic-dev runtime without locking in.** The parity
matrix tells you exactly which features have parity and which don't, so
the runtime decision is reversible.

**Building your own agentic-dev framework.** Use this repo as a
reference implementation. The conventions for agents, skills, hooks,
and eval rubrics are battle-tested.

---

## Repo layout

```text
ai-skills/
├── plugin/                  # Claude Code plugin (canonical for Claude Code)
│   ├── .claude-plugin/      # Plugin manifest + 13 userConfig knobs
│   ├── agents/              # 26 specialized agents
│   ├── skills/              # 73 skills (32 context: fork + 4 main-thread orchestrators + 37 knowledge skills)
│   ├── rules/               # 12 cross-cutting policies
│   ├── hooks/               # 18 hook scripts across 13 lifecycle events
│   ├── eval/                # 45 rubrics + 270 calibration samples + Tier 1/2 runner
│   ├── schemas/             # G7 spawn-payload + return-contract JSON schemas
│   ├── docs/                # Getting-started + workflow + concept docs
│   └── dev/validate.py      # Local validator
├── .agents/skills/          # 39 skills shared by Codex + Windsurf
├── .codex/                  # Codex package (22 roles, 8 rules, operations, templates)
├── .windsurf/               # Windsurf package (22 roles, 39 skills, 27 workflows, hooks)
├── .claude-plugin/          # Marketplace manifest pointing at ./plugin
├── plugin-design/           # Historical Phase 1–2 design docs
├── review/parity-matrix.md  # Cross-package alignment tracker (Codex ↔ Windsurf)
├── AGENTS.md                # Codex root instructions
├── ARCHITECTURE.md          # System design, primitive mapping, install flow
├── CLAUDE.md                # Claude Code root instructions
├── PARITY.md                # Cross-vendor parity model
├── TESTING.md               # Validation approach + hook testing
├── install.sh               # Codex + Windsurf installer (Linux/macOS)
└── install.ps1              # Codex + Windsurf installer (Windows)
```

---

## Status

- **Latest version:** 0.3.10 (see [`plugin/CHANGELOG.md`](./plugin/CHANGELOG.md) for history)
- **License:** [MIT](./LICENSE)
- **Maintainer:** Alex Voloshin
  ([@alex-voloshin-dev](https://github.com/alex-voloshin-dev)) — MS CS in progress
- **Issues / discussion:** open a GitHub issue
- **Updates:** periodic, visible commits weekly

---

## Contributing

Contributions welcome — particularly:

- Eval rubric additions with calibration samples
- Parity-matrix entries for runtimes not yet covered
- Production failure modes / war stories that motivate new hooks or
  rules

Open an issue first to discuss scope. Direct PRs without an issue are
fine for typo / link / small-doc fixes.
