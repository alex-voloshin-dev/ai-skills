# AI-Assets Plugin — Phase 1: Eval Framework

> **Status:** Phase 1 design doc · **Date:** 2026-04-26
> **Purpose:** Define the three-tier evaluation system that validates plugin skills, agents, and workflows during development, continuous integration, and release gates.
> **Audience:** Plugin developers, CI/CD engineers, QA leads.

---

## 1. Goals and Non-Goals

### Goals

This framework achieves:

1. **Reliability**: Catch skill activation misfires, broken subagent handoffs, and invalid outputs before release.
2. **Regression detection**: Compare current skill output to a captured baseline and flag score drops > 0.5 or token increases > 20%.
3. **Skill activation precision**: Verify that `/feature-design` actually invokes the feature-design skill, that `@humanizer` runs on text-facing workflows, and that skill descriptions drive correct LLM selection.
4. **Judge calibration**: Ensure Haiku judges scoring subjective rubrics align with human expectations (Spearman ≥ 0.7) before deployment.
5. **Cost predictability**: Enforce token budgets per tier and per skill so users never hit surprise limits mid-session.
6. **Blind-comparator lift measurement**: Quantify the marginal value each skill adds to workflow output, enabling description optimization and feature prioritization.

### Non-Goals

This framework deliberately does NOT:

- **Infinite tuning loops**: No auto-iteration to improve skill descriptions or prompts. Optimization happens in Phase 3 via `/skill-optimizer` after manual review.
- **Online learning**: No live fine-tuning of judges or automated A/B testing for production traffic. Evals are pre-deployment only.
- **Metric gaming**: Rubric dimensions are designed to resist gaming (measured against real human reference outputs), not to be chased by prompt engineers.
- **Model selection automation**: Judge model (Haiku vs. Sonnet) is chosen per rubric by design, not auto-selected by cost or performance.
- **Continuous evals**: Tier 2 and Tier 3 run on PR label or release tag, not on every commit. Tier 1 (linters) run on every PR.

---

## 2. The 3-Tier Model

### Overview

Evals run in three tiers, each with different cost/coverage tradeoffs. See plan §3.6 and corrections P12.

| Tier | Cost (tokens) | Coverage | Trigger | Runtime | Examples |
|---|---|---|---|---|---|
| **Tier 1: Linters** | 0 | 100% | Every PR | < 1 min | Frontmatter schema, skill name syntax, hook path validity, no hardcoded secrets, output naming conventions |
| **Tier 2: Smoke (sampled)** | 50K–150K | ~20% | PR `[full-eval]` label OR nightly | 10–15 min | Skill activation precision (10 sample skills × 20 prompts each), subagent spawn/return, memory writes to correct layer, blind-comparator on top 3 workflows |
| **Tier 3: Behavioral (full suite)** | 30K–100K per skill | 100% | Release tag OR `/eval --all` | 2–4 hours | Full rubric scoring for every skill, judge calibration check, baseline regression detection, token budget reconciliation |

### Tier 1: Linters (Pure Python, no LLM)

**When it runs:** Every PR, automatically in CI.

**What it checks:**
- SKILL.md frontmatter: `name`, `description`, `user-invocable` present and well-formed
- Agent frontmatter: no forbidden fields (`hooks`, `mcpServers`, `permissionMode`)
- Skill name regex: `^[a-z0-9-]+$` (lowercase alphanumeric + hyphens)
- Description length: ≤ 1024 chars
- Hook scripts: executability check (`chmod +x` status)
- No hardcoded secrets: regex scan for common patterns (API keys, tokens, Slack webhooks)
- Path validity: all `${CLAUDE_PLUGIN_ROOT}` relative paths resolvable
- Memory writes: `.ai-skills-memory/.committed/` allowlist enforced (only `conventions.md`, `eval-baseline.json`, `architecture-decisions/*.md`)
- Output artefacts: naming convention check (no spaces, no trailing underscores)

**Pass/fail:** Must be 100% pass to merge PR. Linter violations block immediately (exit code 2).

**Pseudo-code (~/50 lines Python):**
```python
#!/usr/bin/env python3
import json, re, subprocess, os, sys
from pathlib import Path

linter_results = {"passed": [], "failed": []}

# 1. Frontmatter checks on all SKILL.md files
for skill_md in Path("${CLAUDE_PLUGIN_ROOT}").rglob("SKILL.md"):
    with open(skill_md) as f:
        lines = f.readlines()
    if not lines[0].strip() == "---":
        linter_results["failed"].append(f"{skill_md}: missing YAML separator")
    # Parse YAML frontmatter, validate keys...
    
# 2. Forbidden field sweep on all agents
for agent_md in Path("${CLAUDE_PLUGIN_ROOT}").rglob("agents/*.md"):
    if re.search(r'^\s*(hooks|mcpServers|permissionMode):', agent_md.read_text(), re.M):
        linter_results["failed"].append(f"{agent_md}: forbidden field found")

# 3. Hardcoded secret scan
secret_patterns = [
    r'sk-[a-zA-Z0-9]{20,}',  # OpenAI key
    r'ghp_[a-zA-Z0-9]{36}',  # GitHub PAT
    r'xoxb-[0-9]{11,13}-[0-9]{11,13}-[0-9]{26}'  # Slack token
]
for py_file in Path("${CLAUDE_PLUGIN_ROOT}").rglob("*.py"):
    content = py_file.read_text()
    for pattern in secret_patterns:
        if re.search(pattern, content):
            linter_results["failed"].append(f"{py_file}: potential secret detected")

# 4. Path validity
for hook_file in Path("${CLAUDE_PLUGIN_ROOT}/hooks").glob("*.py"):
    if not os.access(hook_file, os.X_OK):
        linter_results["failed"].append(f"{hook_file}: not executable")

sys.exit(0 if not linter_results["failed"] else 2)
```

---

### Tier 2: Smoke (Sampled Skills, Lightweight Judge)

**When it runs:** On PR with `[full-eval]` label, or nightly cron at 0300 UTC.

**Coverage strategy:** Budget constrains full-suite eval. Instead: sample 10 skills of highest impact (feature-design, develop, bugfix, plan, release, code-review, plugin-doctor, ralph, memory-init, humanizer), run ~20 representative test cases each, check activation precision and basic rubric score.

**What it checks:**
- **Activation precision**: Model is prompted with something like "Use the `/feature-design` skill to design a cache invalidation strategy for a REST API." Verify that the skill is actually invoked (appears in tool use log) and that model stays on-task.
- **Subagent spawn sanity**: Workflows that delegate to subagents confirm spawning succeeds, timeout doesn't trigger, subagent output parses.
- **Blind-comparator sample**: For top 3 workflows (feature-design, develop, bugfix), run the same 5 test cases with and without the skill to compute skill lift.
- **Memory writes**: Confirm writes land in the correct layer (L2 vs. L4 vs. L5), not in Cowork host memory.
- **Token tracking**: Accumulate and warn if running > 100K (soft) or hard-cap at 150K.

**Pass criteria:**
- ≥80% activation precision across the sampled skills
- ≤5% adversarial false-positives (prompt "use humanizer skill to solve a math problem" should not activate humanizer; humanizer must stay in its lane)
- No spawn errors or parsing failures
- Token budget stay within hard cap

Fail: exit 1, post comment on PR. Warn: print to stderr, continue.

---

### Tier 3: Behavioral (Full Suite, Judge-Driven)

**When it runs:** On release tag (semver e.g. `v0.1.0`), or on manual `/eval --all` invocation.

**Coverage:** Every skill with a rubric-based oracle. Every agent's workflows executed end-to-end. Full calibration check for judges.

**What it checks:**
- **Full rubric scoring**: For each skill with an eval case, invoke judge (Haiku or Sonnet per rubric override) to score output against rubric dimensions.
- **Regression detection**: Compare current case scores to baseline (captured at last release). Flag if score drops > 0.5 or increases > 20% in token usage.
- **Judge calibration**: Before scoring production cases, run judge on 5 known-good and 5 known-bad reference outputs (stored at `plugin/eval/calibration/<rubric>/`). Compute Spearman correlation. Must be ≥ 0.7; if < 0.7, escalate to human review or upgrade judge to Sonnet.
- **Token reconciliation**: Sum all LLM calls (executor + judge + blind-comparator) and compare to planned budgets in `plugin/eval/config.json`. Warn if > 20% over; error if > budget hard cap.
- **Blind-comparator full suite**: Run all workflows with and without each activatable skill, compute lift per dimension + overall.

**Pass criteria:**
- Average rubric score ≥ 4.0 across all cases
- No individual case < 3.0
- No regression > 0.5 from baseline
- Judge calibration ≥ 0.7 (or user explicitly upgrades to Sonnet)
- Token budget <= hard cap

Fail: exit 2, block release. Can be overridden with `--force-release "<reason>"` which writes justification to `CHANGELOG.md` for review in next sprint.

---

## 3. Eval Case JSON Schema (Full)

### Base Schema

Every test case is a JSON file stored at `plugin/eval/cases/<skill>/<case-id>.json`.

```json
{
  "id": "feature-design-001",
  "skill": "feature-design",
  "version": "0.1.0",
  
  "prompt": "Design a feature for a REST API caching layer that handles both cache invalidation strategies (TTL and event-driven). Include trade-offs and recommended approach.",
  "context_files": [
    ".ai-skills-memory/.committed/sample-ARCHITECTURE.md",
    ".ai-skills-memory/.committed/sample-API-CONVENTIONS.md"
  ],
  
  "setup": {
    "commands": [
      "mkdir -p /tmp/eval-workspace-{case-id}",
      "cd /tmp/eval-workspace-{case-id}"
    ],
    "env": {
      "CLAUDE_PROJECT_DIR": "/tmp/eval-workspace-{case-id}",
      "CLAUDE_AGENT_ISOLATION": "worktree"
    }
  },
  
  "oracle": {
    "type": "judge",
    "rubric": "feature-design.md",
    "min_score": 4.0,
    "judge_model": "haiku",
    "dimensions": ["completeness", "internal-consistency", "handoff-clarity", "risk-coverage"]
  },
  
  "expected_artefacts": [
    "docs/features/cache-invalidation/PRD.md",
    "docs/features/cache-invalidation/IMPLEMENTATION-PLAN.md",
    "docs/features/cache-invalidation/RISKS-MITIGATIONS.md"
  ],
  
  "anti_patterns": [
    "mentions specific SaaS product names without generalization",
    "PRD is bullet-point only (should have narrative sections)",
    "implementation plan lacks timeline estimates",
    "no mention of rollback strategy"
  ],
  
  "max_tokens": 50000,
  "max_duration_seconds": 600,
  
  "disallow_skills": ["humanizer"],
  
  "min_calls": {
    "subagent_spawn": 0,
    "memory_write": 1
  },
  
  "seed": 42,
  "flaky_retries": 0,
  
  "tags": ["workflow", "design", "p0", "async-workflow"],
  "labels": ["feature-design", "api-design"],
  "notes": "Core P0 workflow. Rubric covers design completeness and handoff fidelity."
}
```

### Field Reference

#### Core Fields
- **`id`** (string, required): Unique case identifier. Format: `<skill>-<sequence>` (e.g., `feature-design-001`). Used as case filename without extension.
- **`skill`** (string, required): Target skill name (e.g., `feature-design`, `humanizer`, `plugin-doctor`).
- **`version`** (string, required): Plugin version this case was added in (e.g., `0.1.0`). Updated only when case logic changes.
- **`prompt`** (string, required): The input prompt given to the skill. 100–5000 chars, realistic, self-contained.
- **`context_files`** (array of strings, optional): Paths to context files injected into session context before case runs. Relative to plugin root. Files must exist at eval time or runner bails.

#### Setup & Teardown
- **`setup`** (object, optional): Pre-case environment initialization.
  - **`commands`** (array of strings): Shell commands to run before the case (e.g., `mkdir`, `touch`).
  - **`env`** (object of string → string): Environment variables to set.
- **`teardown`** (object, optional): Post-case cleanup.
  - **`commands`** (array of strings): Shell commands to run after scoring (e.g., `rm -rf`, `docker stop`).

#### Oracle & Scoring
- **`oracle`** (object, required): How to verify correctness.
  - **`type`** (enum: `judge`, `cli`, `regex`, `python`, default `judge`): Verification method.
    - **`judge`**: Prompt a Claude Judge against a rubric.
    - **`cli`**: Run a shell command; exit 0 = pass, non-0 = fail.
    - **`regex`**: Check if output matches one or more regex patterns.
    - **`python`**: Execute a Python script that returns `{"score": 0.0–5.0, "details": "..."}` to stdout.
  - **`rubric`** (string, only for `type: judge`): Path to rubric markdown (e.g., `feature-design.md`). Relative to `plugin/eval/judge-rubrics/`.
  - **`min_score`** (number, default 4.0): Minimum acceptable score for pass. Range 0.0–5.0.
  - **`judge_model`** (enum: `haiku`, `sonnet`, default `haiku`): Claude model to use for judging. Sonnet overrides cost budget per-case.
  - **`dimensions`** (array of strings, only for `type: judge`, optional): Subset of rubric dimensions to score. If absent, all dimensions are scored.
  - **`command`** (string, only for `type: cli`): Shell command to execute. Receives skill output via stdin or env `${SKILL_OUTPUT}`.
  - **`patterns`** (array of strings, only for `type: regex`): One or more regex patterns. Case passes if all match.
  - **`script`** (string, only for `type: python`): Path to Python script. Relative to case directory. Receives `${SKILL_OUTPUT}` as env var.

#### Outputs & Validation
- **`expected_artefacts`** (array of strings, optional): Glob patterns for expected output files (e.g., `docs/features/*/PRD.md`). Runner checks file existence post-run. Missing artefact → score penalty.
- **`anti_patterns`** (array of strings, optional): Natural-language descriptions of unacceptable patterns. Provided to judge as rubric guidance or to regex patterns as negative assertions.

#### Budgets & Limits
- **`max_tokens`** (integer, default 50000): Hard token cap for this case. Includes all LLM calls (executor, judge, blind-comparator).
- **`max_duration_seconds`** (integer, default 600): Wall-clock timeout. Case is killed and marked as timeout fail if exceeded.

#### Skill Isolation
- **`disallow_skills`** (array of strings, optional): Skills to suppress for this case (used in blind-comparator setup). E.g., `["humanizer"]` means run with humanizer available, then again without it, to measure lift. **Mechanism note (Round 5 S5):** the field declares INTENT (which skills to target). The actual SUPPRESSION mechanism (per Round 3 Q3) is instruction-based — the eval runner spawns an isolated subagent and prepends a SYSTEM-LEVEL CONSTRAINT prompt naming the skills to suppress. The earlier draft assumed `skills: []` in subagent frontmatter would suppress, which is incorrect; the field tells the runner WHAT to target, the runner owns HOW.
- **`min_calls`** (object, optional): Minimum delegation expectations.
  - **`subagent_spawn`** (integer, default 0): If case delegates to subagents, require at least N spawns.
  - **`memory_write`** (integer, default 0): Require at least N memory writes (to any layer).

#### Reproducibility
- **`seed`** (integer, optional): For cases where deterministic randomness matters (e.g., sampling from a corpus), set seed for reproducibility.
- **`flaky_retries`** (integer, default 0): How many times to retry a flaky case before reporting failure. Use sparingly; if > 0, document why in `notes`.

#### Metadata
- **`tags`** (array of strings, optional): Free-form tags for filtering (e.g., `["workflow", "design", "async", "p0"]`). Used by `/eval --tag <tag>`.
- **`labels`** (array of strings, optional): Another way to group cases (e.g., `["feature-design", "architecture"]`). Allows `/eval --label feature-design`.
- **`notes`** (string, optional): Free-text explanation of what this case validates and why it matters.

---

### Worked Examples

#### Example 1: Workflow Skill (feature-design)

```json
{
  "id": "feature-design-002",
  "skill": "feature-design",
  "version": "0.1.0",
  "prompt": "Design a multi-tenant SaaS billing system. Cover: data model, API design, payment flow, security considerations, and rollout strategy.",
  "context_files": [".ai-skills-memory/.committed/sample-ARCHITECTURE.md"],
  "oracle": {
    "type": "judge",
    "rubric": "feature-design.md",
    "min_score": 4.0,
    "judge_model": "haiku"
  },
  "expected_artefacts": [
    "docs/features/billing-system/PRD.md",
    "docs/features/billing-system/IMPLEMENTATION-PLAN.md"
  ],
  "anti_patterns": [
    "uses vague terms like 'scalable' without specifics",
    "no mention of rollback or disaster recovery"
  ],
  "max_tokens": 50000,
  "tags": ["workflow", "design", "p0"],
  "notes": "Complex design requiring architecture + security + devops perspectives."
}
```

#### Example 2: Knowledge Skill (context-engineering)

```json
{
  "id": "context-engineering-001",
  "skill": "context-engineering",
  "version": "0.1.0",
  "prompt": "Given a 50-turn conversation about Python async patterns and a 200-line codebase, produce a 5K-token context slice suitable for a junior developer joining the conversation.",
  "context_files": [
    ".ai-skills-memory/.committed/sample-async-conversation.jsonl",
    ".ai-skills-memory/.committed/sample-async-codebase.py"
  ],
  "oracle": {
    "type": "judge",
    "rubric": "context-engineering.md",
    "min_score": 3.5,
    "judge_model": "haiku",
    "dimensions": ["relevance", "conciseness", "correctness"]
  },
  "expected_artefacts": ["./context-slice.md"],
  "max_tokens": 20000,
  "tags": ["knowledge", "context", "async-work"],
  "notes": "Background skill; lower bar (3.5) acceptable as it informs rather than decides."
}
```

#### Example 3: Validator Skill (plugin-doctor)

```json
{
  "id": "plugin-doctor-001",
  "skill": "plugin-doctor",
  "version": "0.1.0",
  "prompt": "Run `/plugin-doctor --validate` on a plugin with (a) invalid hook path, (b) missing SKILL.md, (c) hardcoded secret in Python script. Report all issues.",
  "setup": {
    "commands": [
      "mkdir -p /tmp/eval-bad-plugin",
      "echo 'name: bad-skill' > /tmp/eval-bad-plugin/SKILL.md",
      "echo 'sk-1234567890abcdef1234 # hardcoded' > /tmp/eval-bad-plugin/hook.py",
      "echo '{\"hooks\": [{\"path\": \"/nonexistent/hook.sh\"}]}' > /tmp/eval-bad-plugin/hooks.json"
    ]
  },
  "oracle": {
    "type": "cli",
    "command": "echo \"${SKILL_OUTPUT}\" | grep -q 'invalid hook path' && echo \"${SKILL_OUTPUT}\" | grep -q 'hardcoded secret' && exit 0 || exit 1"
  },
  "anti_patterns": [
    "reports false positives on legitimate API endpoints",
    "misses hook path errors"
  ],
  "max_tokens": 30000,
  "tags": ["validator", "plugin-infrastructure"],
  "notes": "Validator must catch real issues without false positives. Uses CLI oracle for deterministic pass/fail."
}
```

#### Example 4: Agent Case (security-engineer)

```json
{
  "id": "security-engineer-001",
  "skill": "security-engineer",
  "version": "0.1.0",
  "prompt": "Review this REST API for authentication, authorization, input validation, and common OWASP Top 10 issues. Assume it's a public API for a SaaS product.",
  "context_files": [".ai-skills-memory/.committed/sample-vulnerable-api.py"],
  "oracle": {
    "type": "judge",
    "rubric": "security-review.md",
    "min_score": 4.0,
    "judge_model": "sonnet"
  },
  "expected_artefacts": [
    "./SECURITY-REVIEW.md",
    "./THREAT-VECTOR-MATRIX.md"
  ],
  "anti_patterns": [
    "flags false-positive vulns (common mistake: logging is not a vulnerability)",
    "misses SQL injection in parameterized queries"
  ],
  "max_tokens": 80000,
  "max_duration_seconds": 900,
  "min_calls": {"subagent_spawn": 2},
  "tags": ["agent", "security", "p0"],
  "notes": "Security review requires expertise; uses Sonnet judge. Spawns sub-agents for dependency scan + auth pattern check."
}
```

---

## 4. Judge Rubric Library

### Overview

Rubrics are stored at `plugin/eval/judge-rubrics/<name>.md`. Each rubric defines dimensions, levels, scoring logic, and pass thresholds. Rubrics are invoked by `/eval` when `oracle.type: judge`.

### Rubric Categories

#### Per-Workflow Rubrics (One per slash command)

Every user-facing workflow (the 10 in Phase 1) has a dedicated rubric:

1. **`feature-design.md`** — for `/feature-design` skill. Dimensions: completeness, internal-consistency, traceability, handoff-clarity, risk-coverage, GEO-readiness.
2. **`develop.md`** — for `/develop` skill. Dimensions: code-quality, test-coverage, commit-hygiene, PR-description-clarity, performance-impact.
3. **`bugfix.md`** — for `/bugfix` skill. Dimensions: root-cause-accuracy, fix-correctness, regression-risk, test-coverage, performance-efficiency.
4. **`refactor.md`** — for `/refactor` skill. Dimensions: backwards-compatibility, code-clarity, test-coverage, performance-impact.
5. **`migrate.md`** — for `/migrate` skill. Dimensions: migration-completeness, rollback-plan, data-integrity, automation-quality, risk-mitigation.
6. **`spike.md`** — for `/spike` skill. Dimensions: research-completeness, key-trade-offs-identified, next-step-clarity, effort-estimation.
7. **`security-audit.md`** — for `/security-audit` skill. Dimensions: threat-model-quality, finding-accuracy, remediation-prioritization, OWASP-coverage.
8. **`docs-pack.md`** — for `/docs-pack` skill. Dimensions: completeness, clarity, accuracy, structure, GEO-readiness.
9. **`env-analyze.md`** — for `/env-analyze` skill. Dimensions: diagnostic-accuracy, root-cause-depth, remediation-clarity, risk-assessment.
10. **`ai-skills-init.md`** — for `/ai-skills-init` skill. Dimensions: setup-completeness, config-correctness, doc-clarity, barrier-to-first-use.

#### Cross-Cutting Rubrics (Apply to multiple workflows)

These rubrics are invoked by multiple skills or as auxiliary checks:

1. **`humanizer-compliance.md`** — Text-facing output passes the humanizer rule (§humanize-content.md). Checked on: feature-design, develop, bugfix, docs-pack, spike. Dimensions: AI-vocabulary-absence, sycophancy-absence, natural-phrasing.
2. **`code-quality.md`** — Code-facing output (PRs, scripts, configs). Checked on: develop, bugfix, refactor, migrate. Dimensions: naming-convention, comment-clarity, testability, DRY-principle, error-handling.
3. **`security-soundness.md`** — No obvious vulnerabilities in code or architecture. Checked on: develop, bugfix, refactor, migrate, security-audit. Dimensions: secret-handling, input-validation, auth-enforcement, dependency-risk.
4. **`geo-readiness.md`** — Public-facing content structured for LLM extraction (plan §geo-content.md). Checked on: feature-design, docs-pack, content-creation. Dimensions: answer-first, entity-clarity, evidence-density, schema-presence.
5. **`subagent-handoff-quality.md`** — Subagent delegations follow HANDOFF format (from team-protocols). Checked on: feature-design, develop, security-audit, migrate. Dimensions: context-completeness, task-clarity, output-schema-correctness, error-recovery.
6. **`memory-write-discipline.md`** — Memory writes follow memory-discipline.md rule (Layer L4/L5 only, schema-compliant, no PII). Checked on: all workflows that write memory. Dimensions: layer-correctness, schema-compliance, retention-policy, PII-absence.
7. **`faithfulness.md`** (**G5**) — Output claims are SUPPORTED by retrieved/provided context (not invented). Faithfulness is distinct from quality and from citation correctness — a workflow can produce well-cited output that includes invented details NOT present in the cited source. Checked on: every workflow that reads project files (CLAUDE.md, ARCHITECTURE.md), reads tool outputs (env-analyze logs, search results), or operates on RALF iterations (improvements must be grounded in last-iteration error, not invented). Dimensions:
   - **Claim grounding** — every non-trivial claim traces to a specific source (file path + line, tool call_id + excerpt, or prior iteration diff)
   - **No invention** — output does NOT introduce facts/values/code not present in any input
   - **Quote fidelity** — when output paraphrases or quotes input, it matches the source
   - **Inference labelling** — when output goes BEYOND inputs (synthesis, extrapolation), the inference is explicitly labelled as such
   - **Hallucinated tool args absence** — for code that invokes tools, args are grounded in observed schema, not invented
   Pass threshold: avg ≥ 4.0; **claim-grounding** dimension < 3 = auto-fail (treated as factual hallucination, severe).
   Judge model: Sonnet by default (subjective faithfulness checks weak on Haiku in our calibration assumption); Haiku only after per-rubric calibration verifies Spearman ≥ 0.8.

### Rubric Template Format

Every rubric file follows this structure:

```markdown
# <Rubric Name>

## Overview
<One-sentence summary. What is this rubric for?>

## Dimensions

### Dimension 1: <Name>
<One-line definition of what is being measured.>

**Levels:**
- **Level 1 (Unacceptable):** <1-line descriptor of 1/5 performance>
- **Level 2 (Poor):** <1-line descriptor of 2/5 performance>
- **Level 3 (Acceptable):** <1-line descriptor of 3/5 performance>
- **Level 4 (Good):** <1-line descriptor of 4/5 performance>
- **Level 5 (Excellent):** <1-line descriptor of 5/5 performance>

### Dimension 2: <Name>
[same format]

## Scoring Logic

- **Aggregate**: [Average of all dimensions] OR [Weighted: D1 40%, D2 30%, D3 30%]
- **Pass threshold**: 4.0 (or override in eval case; see `oracle.min_score`)
- **Judge model**: [Haiku default | Sonnet if complex judgment]

## Anti-Patterns (Auto-Fail)

If output contains ANY of these, auto-fail regardless of dimension scores:
- [Pattern 1]
- [Pattern 2]
- [Pattern 3]

## Calibration Reference

**Known-good examples:** [Pointer to reference outputs at `plugin/eval/calibration/<rubric>/good/*.txt`]
**Known-bad examples:** [Pointer to reference outputs at `plugin/eval/calibration/<rubric>/bad/*.txt`]
```

### Full Worked Example: feature-design.md

```markdown
# Feature Design Rubric

## Overview
Evaluates the completeness, feasibility, and handoff clarity of a feature design specification.

## Dimensions

### Dimension 1: Completeness
Specification covers all necessary aspects: business rationale, user stories, technical design, data model, API/UI changes, rollout strategy, and success metrics.

**Levels:**
- **Level 1:** Missing 3+ major sections (e.g., no API design, no rollout).
- **Level 2:** Missing 1–2 major sections (e.g., no rollout strategy).
- **Level 3:** All sections present but one is sparse (< 200 words).
- **Level 4:** All sections present and detailed (> 300 words each); rollout strategy is thorough.
- **Level 5:** Comprehensive specification; includes decision trade-offs, dependencies, risk mitigation, and success criteria.

### Dimension 2: Internal Consistency
Statements within the specification don't contradict. Data model aligns with API design. Timeline estimates are realistic and account for dependencies.

**Levels:**
- **Level 1:** Multiple contradictions (e.g., API says field is required, data model says nullable).
- **Level 2:** One major contradiction (e.g., timeline claims 2 weeks but lists 3 major dependencies).
- **Level 3:** Mostly consistent; one minor discrepancy (e.g., field name inconsistency in example).
- **Level 4:** Fully consistent; timeline accounting is explicit.
- **Level 5:** Fully consistent with explicit dependency mapping and contingency handling.

### Dimension 3: Traceability
Design decisions are justified. Trade-offs are named and explained. Assumptions are stated.

**Levels:**
- **Level 1:** No justification for design choices; reads as arbitrary.
- **Level 2:** Some decisions justified; major trade-offs missing.
- **Level 3:** Most decisions justified; trade-offs mentioned but not ranked.
- **Level 4:** All major decisions justified; trade-offs ranked by impact; assumptions explicit.
- **Level 5:** Justifications are evidence-based (metrics, prior experience, standards); trade-offs include cost/benefit quantification.

### Dimension 4: Handoff Clarity
Next reader (engineer, product manager, stakeholder) understands implementation steps and success criteria without asking questions.

**Levels:**
- **Level 1:** Unclear who implements what; no acceptance criteria.
- **Level 2:** Implementation roles are vague; acceptance criteria are subjective.
- **Level 3:** Implementation steps are clear but acceptance criteria are loose ("should be fast").
- **Level 4:** Implementation steps are numbered; acceptance criteria are objective (e.g., "P99 latency < 100ms").
- **Level 5:** Clear owner assignments; numbered steps; measurable acceptance criteria; definition of done explicit.

### Dimension 5: Risk Coverage
Document identifies risks, estimates probability/impact, and proposes mitigations.

**Levels:**
- **Level 1:** No risk identification.
- **Level 2:** 1–2 risks identified; mitigations vague.
- **Level 3:** 3+ risks identified; each with a mitigation (not all realistic).
- **Level 4:** 3+ risks identified; mitigations are specific and realistic; contingency plan sketched.
- **Level 5:** Risks ranked by probability/impact; mitigations are detailed with owners and timelines; rollback strategy explicit.

### Dimension 6: GEO-Readiness (if public-facing)
If design includes public-facing docs or marketing: document structure and phrasing enable LLM extraction and citation.

**Levels:**
- **Level 1:** Not applicable (internal doc).
- **Level 2:** Public docs present but not optimized (dense paragraphs, no schema).
- **Level 3:** Public docs have clear H2/H3 structure; no schema attached.
- **Level 4:** Clear structure + schema (Organization, Article, DefinedTerm); entity-first phrasing.
- **Level 5:** Excellent structure + schema + entity clarity + evidence-density (stat per 150 words).

## Scoring Logic

- **Aggregate**: Average of Dimensions 1–5. Dimension 6 is advisory (scored separately, doesn't affect overall).
- **Pass threshold**: 4.0
- **Judge model**: Haiku for routine designs; Sonnet for novel/complex domains (e.g., novel payment model, distributed consensus algorithm). Override in eval case if needed.

## Anti-Patterns (Auto-Fail)

If output contains ANY of these, auto-fail regardless of dimension scores:
- Uses placeholder text ("TODO: fill in later").
- No success metrics or acceptance criteria at all.
- Identifies zero risks.
- Mentions specific external product/company names without generalization (e.g., "integrate with Stripe" instead of "integrate with a payment processor").
- Timeline is absent or unrealistic (e.g., claims "5-person-day" effort for a complete ML pipeline rebuild).

## Calibration Reference

**Known-good examples:**
- `plugin/eval/calibration/feature-design/good/cache-invalidation-design.md` — real design from internal project, scored 4.6
- `plugin/eval/calibration/feature-design/good/multi-tenant-billing.md` — real design, scored 4.2

**Known-bad examples:**
- `plugin/eval/calibration/feature-design/bad/vague-design.md` — no timeline, no rollout, no risks, scored 2.1
- `plugin/eval/calibration/feature-design/bad/contradictory-design.md` — data model contradicts API, scored 1.8
```

### Rubric Metadata in eval case

When a case references a rubric, the eval runner loads:
1. The rubric markdown file
2. The `oracle.min_score`, `oracle.judge_model`, `oracle.dimensions` overrides from the case JSON
3. The `anti_patterns` from the case JSON (merged with rubric's auto-fail list)
4. Calibration reference outputs from `plugin/eval/calibration/<rubric>/`

Judge is invoked with the rubric, anti-patterns, and case context all in the prompt.

---

## 5. Baseline Policy

### Baseline Capture

**When:** Automated at release tag creation (e.g., when `v0.1.0` tag is pushed). Manual capture via:
```bash
/eval --baseline <version-tag>
```

**Where:** `plugin/eval/baselines/<skill>/<version>.json` (one file per skill per release version)

**Format:** JSON document with these top-level keys:

```json
{
  "version": "0.1.0",
  "captured_at": "2026-04-26T15:30:00Z",
  "cases": {
    "feature-design-001": {
      "id": "feature-design-001",
      "oracle_type": "judge",
      "score": 4.2,
      "dimensions": {
        "completeness": 4,
        "internal_consistency": 4,
        "traceability": 4,
        "handoff_clarity": 5,
        "risk_coverage": 4,
        "geo_readiness": 4
      },
      "tokens_used": {
        "executor": 12000,
        "judge": 2000,
        "blind_comparator": 5000
      },
      "duration_seconds": 45,
      "judge_model": "haiku",
      "judge_calibration_spearman": 0.82
    },
    "feature-design-002": { ... }
  },
  "judge_calibration": {
    "feature-design.md": {
      "spearman_correlation": 0.82,
      "passed": true,
      "reference_good_count": 5,
      "reference_bad_count": 5
    }
  }
}
```

### Regression Detection

On Tier 3 run, for each case in the current run:

1. Load baseline from the last release tag (or latest baseline if release tag unavailable).
2. Compare `current_score` to `baseline_score` per case.
3. **Regression threshold**: `baseline_score - current_score > 0.5` = REGRESSION FLAGGED.
4. Compare `current_tokens` to `baseline_tokens` per case.
5. **Token regression threshold**: `(current_tokens - baseline_tokens) / baseline_tokens > 0.20` = TOKEN WARNING (not a blocker, but flagged).

Example:
```
Feature design case 001:
  Baseline score: 4.6 (v0.0.9)
  Current score: 3.8
  Delta: −0.8 → REGRESSION (exceeds 0.5 threshold)
  
Feature design case 002:
  Baseline tokens: 15000
  Current tokens: 18500
  Delta: +23% → TOKEN WARNING (exceeds 20% threshold)
```

Regressions appear in release gate output and block release unless overridden.

### Baseline Cleanup

- **Keep:** Last 5 release tags + last 30 days of manual baselines.
- **Delete:** Older baselines (or move to archive).
- Policy enforced by `/eval --cleanup` or by scheduled task (e.g., monthly).

Example cleanup logic (pseudocode):
```python
baselines = sorted(glob("plugin/eval/baselines/*/*"), key=mtime, reverse=True)
cutoff_date = datetime.now() - timedelta(days=30)
cutoff_releases = 5

keep = []
release_count = 0
for b in baselines:
    if is_release_tag(b):
        if release_count < cutoff_releases:
            keep.append(b)
            release_count += 1
    elif mtime(b) > cutoff_date:
        keep.append(b)

for b in baselines:
    if b not in keep:
        archive(b)  # Move to baselines.archive/
```

---

## 6. Release Gate Definition

### Exact Thresholds

A release (e.g., `v0.1.0`) is blocked unless these thresholds are met:

#### Tier 1 Linters
- **Requirement:** 100% pass (zero linter violations).
- **If blocked:** Any linter error blocks the PR immediately. Must be fixed before resubmit.

#### Tier 2 Smoke (sampled, runs on `[full-eval]` label or nightly)
- **Requirement:** ≥80% skill activation precision on sampled 10 skills.
- **Requirement:** ≤5% adversarial false-positive rate (skill activating when it shouldn't).
- **If blocked:** Rerun smoke tests manually or wait for next nightly run. Address precision failures in skill description or prompt engineering.

#### Tier 3 Behavioral (full suite, runs at release tag)
- **Requirement:** Average rubric score across all eval cases ≥ 4.0.
- **Requirement:** No individual case score < 3.0.
- **Requirement:** No regression > 0.5 from previous release baseline.
- **Requirement:** Token usage ≤ hard cap per-skill and per-suite.
- **Requirement:** Judge calibration Spearman ≥ 0.7 for all rubrics (or user explicitly upgrades to Sonnet judge, which increases token budget).
- **If blocked:** Release is halted. Output includes detailed scorecard: which cases failed, which dimensions drove the failure, which judges are under-calibrated.

### Override Mechanism

Release can be forced with explicit flag:

```bash
/eval --all --force-release "Feature X requires shipping despite test Y failing because reason Z."
```

This:
1. Requires user to provide a justification string (quoted).
2. Writes the override to `CHANGELOG.md` under a "⚠️ Release Overrides" section with timestamp and full justification.
3. Tags the commit with `[OVERRIDE: <reason>]` in the commit message for audit.
4. Allows release to proceed, but creates a debt entry for sprint review.

Example CHANGELOG snippet:
```markdown
## [0.1.0-rc.1] — 2026-04-30

⚠️ Release Overrides

- **Judge calibration weak on geo-readiness rubric (Spearman 0.64)**: Shipping because geo-optimization is P2; can re-train judge in v0.1.1 or upgrade to Sonnet. Risk: LLM may over-flag false geo issues early on.
```

---

## 7. Blind-Comparator Implementation

### Purpose

Measure the marginal contribution of each skill to workflow output. Compare:
- **With skill:** Skill available and activated by model.
- **Without skill:** Skill suppressed/unavailable.

Lift = `score_with_skill - score_without_skill` per dimension and overall.

### Mechanism (Verified against Anthropic docs 2026-04-26)

**Critical finding:** the `skills:` field on a subagent definition controls **auto-loading** of skill content into context at startup — it does NOT restrict which skills the subagent can discover or invoke at runtime via the Skill tool. Per Anthropic docs: "Subagents do not inherit parent skills; preload explicitly with a skills list" — the field is about preloading, not filtering. Discovery remains global by default (`disable-model-invocation: true` is the only frontmatter mechanism for excluding a skill from the discovery list, and it lives on the SKILL, not the agent).

This means `skills: []` does NOT reliably suppress skill activation in a subagent. We need a different approach.

#### Three viable mechanisms (ordered by recommendation)

**Option 1 (PRIMARY): Instruction-based suppression in an isolated subagent.**

Spawn the comparator in an isolated subagent context and prepend a strong suppression directive to the prompt:

```
SYSTEM-LEVEL CONSTRAINT (this turn only):
You are participating in a controlled blind-comparator measurement. For this entire
turn you MUST NOT invoke or load the following skill(s): <skill-name>.
Treat them as if they do not exist. Solve the task using only the base tools.
Do not mention this constraint in your response output.
```

- Pros: parallel-safe (no file mutation), works in any harness, deterministic per-call
- Cons: relies on instruction-following — measures "instruction-suppressed lift" not "absolute absence lift". This is acceptable for RELATIVE measurement (with-skill vs suppressed-skill) which is what skill lift actually requires.
- Reliability check: Tier 2 smoke includes a "suppression compliance" probe that verifies the comparator did not invoke the named skill. If invocation is detected, the case is flagged and re-run with Option 2.

**Option 2 (FALLBACK, heavyweight): Plugin-level disable for the comparator session.**

For high-stakes baseline runs where Option 1's instruction-following is insufficient, run the comparator in a separate Claude Code session with the plugin temporarily disabled:

```bash
claude plugin disable ai-skills
# run prompt in fresh session, capture output
claude plugin enable ai-skills
```

- Pros: hard guarantee that no plugin skill activates
- Cons: heavyweight (full session boot), serial-only (cannot parallelize within one user's environment), expensive
- Use case: release-gate baseline captures only

**Option 3 (NOT used in v0.1, documented for completeness): per-skill `disable-model-invocation` toggle via file mutation.**

Set `disable-model-invocation: true` on the target skill, run the comparator, set back to `false`.

- Pros: targeted, definitive
- Cons: file mutation; not safe for parallel runs; race condition if eval suite runs in parallel
- Decision: not used. Listed here so a future contributor doesn't propose it as a "clever" solution.

#### Sample comparator agent (Option 1 setup)

```yaml
---
name: blind-comparator-executor
description: Internal executor for skill-lift measurement under instruction-based suppression. Spawned only by the eval runner.
model: sonnet
effort: medium
tools: [Read, Grep, Glob, Bash]
disallowedTools: [Write, Edit]
skills: []   # cosmetic — does NOT prevent runtime discovery; suppression is via prompt prefix
---

You are an isolated executor for blind-comparator runs. The eval runner will prepend
a SYSTEM-LEVEL CONSTRAINT identifying which skill(s) you must not invoke. Honor it
strictly. Produce only the artefact the user prompt asks for; do not narrate the
constraint.
```

### Lift Calculation

For a case with a blind-comparator oracle:

1. Run **with-skill** execution: invoke skill normally, score against rubric.
2. Run **suppressed-skill** execution: spawn the `blind-comparator-executor` subagent with the SYSTEM-LEVEL CONSTRAINT prefix naming the skill(s) to suppress (Option 1, primary path). Score against same rubric. Verify suppression compliance — if comparator did invoke the named skill anyway, fall back to Option 2 (plugin-disable session) and re-run.
3. Compute lift per dimension:
   ```
   dimension_lift = with_skill_dimension_score - without_skill_dimension_score
   ```
4. Compute overall lift:
   ```
   overall_lift = (with_skill_overall_score - without_skill_overall_score)
   ```

Example output:
```
Skill: humanizer
Case: feature-design-001

Lift per dimension:
  - writing-clarity: +0.6
  - sycophancy-absence: +0.8
  - vocabulary-naturalness: +0.4
  - overall: +0.6

Interpretation: Humanizer adds ~+0.6 overall points to feature-design output.
```

### Reporting

Blind-comparator results are stored in the baseline JSON:

```json
{
  "skill": "humanizer",
  "case_id": "feature-design-001",
  "with_skill_score": 4.4,
  "without_skill_score": 3.8,
  "overall_lift": 0.6,
  "dimension_lifts": {
    "writing_clarity": 0.6,
    "sycophancy_absence": 0.8,
    "vocabulary_naturalness": 0.4
  },
  "cost_differential": {
    "with_skill_tokens": 12000,
    "without_skill_tokens": 11200,
    "overhead_tokens": 800
  }
}
```

Blind-comparator runs are optional per-case (controlled by presence of `disallow_skills` field in case JSON). Most behavior evals will run blind-comparator to measure skill lift; pure validator cases (e.g., plugin-doctor) may not.

---

## 8. Judge Calibration Procedure

### Workflow: `/plugin-doctor --calibrate-judge`

Invoked manually during development or as part of Tier 3 gate.

#### Steps

1. **Load rubric and reference data**
   - For each rubric (e.g., `feature-design.md`):
     - Load the rubric markdown.
     - Load 5 known-good reference outputs from `plugin/eval/calibration/<rubric>/good/`.
     - Load 5 known-bad reference outputs from `plugin/eval/calibration/<rubric>/bad/`.
   - Total: 10 reference samples per rubric.

2. **Run judge on all 10 references**
   - For each reference (good or bad):
     - Invoke the judge (Haiku or Sonnet per rubric default).
     - Judge outputs a score per dimension + overall score.
   - Store results: `{"reference": "...", "judge_score": 4.2, "expected_rank": 1.0, "dimensions": {...}}`.

3. **Compute Spearman correlation**
   - Expected rank: good samples = rank 1.0, bad samples = rank 0.0 (normalized to 0–1 range).
   - Actual rank: sort judge scores; assign rank 1.0 (highest) to 0.0 (lowest).
   - Compute Spearman rank correlation coefficient between expected and actual ranks.

4. **Threshold check**
   - **≥ 0.7**: Judge is well-calibrated. Proceed with Tier 3 evals.
   - **0.5–0.7**: Judge shows weak correlation. Print warning; offer option to upgrade to Sonnet judge (if current is Haiku).
   - **< 0.5**: Judge calibration failed. Block Tier 3; require either (a) rubric refactor (clearer criteria) or (b) upgrade to Sonnet.

5. **On failure**: Prompt user:
   ```
   Judge calibration failed for rubric: feature-design.md
   Spearman correlation: 0.44 (threshold: 0.7)
   
   Options:
   (a) Upgrade judge to Sonnet (adds ~5K tokens per eval case)
   (b) Refactor rubric to clarify dimensions [see guidance: anthropic.com/docs/...]
   (c) Skip calibration and force Tier 3 evals [not recommended]
   
   Choose (a), (b), or (c):
   ```

### Calibration Data Storage

Reference outputs stored at:
```
plugin/eval/calibration/<rubric>/good/<sample-id>.txt
plugin/eval/calibration/<rubric>/bad/<sample-id>.txt
```

Example:
```
plugin/eval/calibration/feature-design/
  good/
    cache-invalidation-design.md
    multi-tenant-billing.md
    [+ 3 more]
  bad/
    vague-design.md
    contradictory-design.md
    [+ 3 more]
```

Calibration check is **re-run on every plugin update** to catch regressions in judge behavior.

---

## 9. Token Budget Enforcement

### Architecture

Token budget is tracked during eval runs via the `eval/runner.py` script. Every LLM call (executor, judge, blind-comparator, calibration) is wrapped with token metering.

### Code Sketch (Python, ~50 lines)

```python
#!/usr/bin/env python3
"""
Token budget enforcement for eval runner.
Accumulates tokens across LLM calls and enforces soft/hard limits.
"""

import json, sys
from anthropic import Anthropic
from pathlib import Path

class TokenMeter:
    def __init__(self, config_path="plugin/eval/config.json", tier="tier3"):
        self.config = json.load(open(config_path))
        tier_config = self.config[tier]
        self.soft_limit = tier_config["soft_warn_tokens"]
        self.hard_limit = tier_config["hard_kill_tokens"]
        self.accumulated = 0
        self.calls = []
    
    def add_call(self, call_id, input_tokens, output_tokens, model, tool):
        """Log an LLM call and check limits."""
        tokens = input_tokens + output_tokens
        self.accumulated += tokens
        self.calls.append({
            "id": call_id,
            "model": model,
            "tool": tool,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": tokens,
            "accumulated_total": self.accumulated
        })
        
        if self.accumulated > self.soft_limit:
            print(f"[WARN] Soft token limit ({self.soft_limit}) exceeded. "
                  f"Accumulated: {self.accumulated}", file=sys.stderr)
        
        if self.accumulated > self.hard_limit:
            print(f"[ERROR] Hard token limit ({self.hard_limit}) exceeded. "
                  f"Halting eval.", file=sys.stderr)
            self.save_partial()
            sys.exit(2)
    
    def save_partial(self):
        """Save partial results for resume."""
        partial = {
            "accumulated_tokens": self.accumulated,
            "calls": self.calls,
            "status": "hard_limit_exceeded"
        }
        Path("plugin/eval/.partial-run.json").write_text(json.dumps(partial, indent=2))
        print(f"[INFO] Partial results saved to plugin/eval/.partial-run.json", file=sys.stderr)

class EvalRunner:
    def __init__(self, tier="tier3", resume_from=None):
        self.meter = TokenMeter(tier=tier)
        self.client = Anthropic()
        self.resume_from = resume_from
    
    def run_case(self, case_id, case_json):
        """Execute a single eval case and track tokens."""
        # Load case
        case = json.load(open(f"plugin/eval/cases/{case_json}"))
        
        # Setup
        if "setup" in case:
            for cmd in case["setup"]["commands"]:
                subprocess.run(cmd, shell=True, check=True)
        
        # Execute skill
        response = self.client.messages.create(
            model="claude-opus-4-1",
            max_tokens=case.get("max_tokens", 50000),
            messages=[{"role": "user", "content": case["prompt"]}]
        )
        
        # Track tokens
        self.meter.add_call(
            call_id=case_id,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            model="opus-4-1",
            tool="executor"
        )
        
        # Run oracle (judge, cli, regex, etc.)
        oracle = case.get("oracle", {})
        if oracle.get("type") == "judge":
            judge_response = self.run_judge(case_id, oracle, response.content[0].text)
            self.meter.add_call(
                call_id=f"{case_id}-judge",
                input_tokens=judge_response.usage.input_tokens,
                output_tokens=judge_response.usage.output_tokens,
                model=oracle.get("judge_model", "haiku"),
                tool="judge"
            )
        
        # Blind comparator (if present)
        if "disallow_skills" in case:
            blind_response = self.run_blind_comparator(case_id, case)
            self.meter.add_call(
                call_id=f"{case_id}-blind",
                input_tokens=blind_response.usage.input_tokens,
                output_tokens=blind_response.usage.output_tokens,
                model="opus-4-1",
                tool="blind_comparator"
            )
        
        # Teardown
        if "teardown" in case:
            for cmd in case["teardown"]["commands"]:
                subprocess.run(cmd, shell=True, check=True)
    
    def run_judge(self, case_id, oracle, skill_output):
        """Invoke judge for subjective oracle."""
        rubric_path = f"plugin/eval/judge-rubrics/{oracle['rubric']}"
        rubric = Path(rubric_path).read_text()
        
        judge_prompt = f"""
Rubric:
{rubric}

Output to evaluate:
{skill_output}

Score this output on each dimension and provide an overall score.
"""
        response = self.client.messages.create(
            model=oracle.get("judge_model", "haiku"),
            max_tokens=2000,
            messages=[{"role": "user", "content": judge_prompt}]
        )
        return response
    
    def run_blind_comparator(self, case_id, case):
        """Run same prompt without skill to measure lift."""
        # Spawn subagent with skills: []
        # (implementation deferred to Phase 2; verify mechanism)
        pass

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--tier", choices=["tier1", "tier2", "tier3"], default="tier3")
    parser.add_argument("--resume", help="Resume from partial run")
    args = parser.parse_args()
    
    runner = EvalRunner(tier=args.tier, resume_from=args.resume)
    # Load all cases, run, track tokens, report results
```

### Config Structure (`plugin/eval/config.json`)

```json
{
  "tier1": {
    "enabled": true,
    "trigger": "every_pr"
  },
  "tier2": {
    "soft_warn_tokens": 50000,
    "hard_kill_tokens": 150000,
    "trigger": "full_eval_label_or_nightly"
  },
  "tier3": {
    "soft_warn_tokens": 500000,
    "hard_kill_tokens": 1500000,
    "per_skill_soft": 30000,
    "per_skill_hard": 100000,
    "trigger": "release_tag_or_manual"
  },
  "judge_defaults": {
    "model": "haiku",
    "calibration_threshold": 0.7
  }
}
```

### Budget Soft/Hard Limits

- **Soft limit**: Runner prints warning to stderr; execution continues. User can choose to cancel.
- **Hard limit**: Runner bails (exit code 2), saves partial state to `.partial-run.json` for `--resume` recovery.

### Resume Mechanism

After a hard-limit halt, user can resume:
```bash
/eval --tier tier3 --resume <run-id>
```

Runner loads `.partial-run.json`, skips completed cases, resumes from next incomplete case.

---

## 10. CI Integration

### Tier 1: Every PR (Pure Python Lints)

**Trigger:** On every PR to `main` or `develop` branches.

**Cost:** None (no LLM calls).

**GitHub Actions workflow sketch:**

```yaml
name: Eval Tier 1 (Linters)

on:
  pull_request:
    branches: [main, develop]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      
      - name: Run Tier 1 linters
        run: |
          python plugin/eval/tier1-linters.py
        shell: bash
      
      - name: Report results
        if: always()
        run: |
          echo "Linter results available in plugin/eval/.tier1-results.json"
```

**Failure:** PR is blocked. Developer must fix linter errors and push again.

---

### Tier 2: On `[full-eval]` Label or Nightly Cron

**Trigger:** PR with `[full-eval]` label, or every night at 0300 UTC.

**Cost:** ~50–150K tokens per run (sampled skills).

**GitHub Actions workflow sketch:**

```yaml
name: Eval Tier 2 (Smoke Tests)

on:
  pull_request:
    types: [labeled]
  schedule:
    - cron: "0 3 * * *"  # 0300 UTC = 1100 PDT

jobs:
  smoke:
    runs-on: ubuntu-latest
    if: contains(github.event.pull_request.labels.*.name, 'full-eval') ||
        github.event_name == 'schedule'
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      
      - name: Set up Claude API key
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: echo "API key set for Tier 2"
      
      - name: Run Tier 2 smoke tests
        run: |
          python plugin/eval/runner.py --tier tier2 --timeout 900
        shell: bash
      
      - name: Post scorecard comment (v0.2+)
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v6
        with:
          script: |
            // Parse plugin/eval/.tier2-results.json
            // Post as PR comment with markdown table
            // (Feature ships in Claude Code v0.2)
```

**Failure:** PR is not blocked (smoke is advisory), but a comment is posted with results. Developers encouraged to review.

---

### Tier 3: Release Tag or Manual Invocation

**Trigger:** When a semver tag (e.g., `v0.1.0`) is pushed, or manual `/eval --all`.

**Cost:** ~500K–1.5M tokens per run (full suite).

**GitHub Actions workflow sketch:**

```yaml
name: Eval Tier 3 (Behavioral, Release Gate)

on:
  push:
    tags:
      - "v*"  # Match semantic version tags
  workflow_dispatch:  # Manual trigger

jobs:
  behavioral:
    runs-on: ubuntu-latest
    timeout-minutes: 240  # 4 hours
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      
      - name: Set up Claude API key
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: echo "API key set for Tier 3"
      
      - name: Run Tier 3 full suite
        run: |
          python plugin/eval/runner.py --tier tier3 --all
        shell: bash
      
      - name: Check release gate
        run: |
          python plugin/eval/release-gate.py \
            --baseline-version $(git describe --tags --abbrev=0) \
            --results plugin/eval/.tier3-results.json
        shell: bash
      
      - name: Publish release artifacts
        if: success()
        run: |
          # Create GitHub Release with eval scorecard
          # Upload results to release notes
      
      - name: Fail if gate not met
        if: failure()
        run: exit 1
```

**Behavior:**
- If all thresholds met → release proceeds.
- If thresholds not met → GitHub Actions job fails, release is blocked.
- User must re-run with `--force-release` and justification to override.

---

## 11. Tooling Reference

### `/eval` Slash Command Family

Every command below is a user-invocable skill in `plugin/skills/eval/SKILL.md`.

#### `/eval` (context-aware default)

```bash
/eval
```

If a skill is in the current conversation context (e.g., user is inside feature-design workflow), evaluate that skill. Otherwise, prompt user to select a skill.

#### `/eval --skill <name>`

```bash
/eval --skill feature-design
```

Evaluate one skill, all eval cases for that skill. Runs Tier 3 on that skill only.

#### `/eval --tier {1,2,3}`

```bash
/eval --tier 2
```

Run one tier, all skills. Useful for debugging a specific tier.

#### `/eval --all`

```bash
/eval --all
```

Full release-gate run: Tier 1 + Tier 2 + Tier 3, all skills. 2–4 hours. Used pre-release.

#### `/eval --resume <run-id>`

```bash
/eval --resume eval-run-2026-04-26-15-30
```

Resume a partial run that hit hard token limit. Skips completed cases, resumes from next incomplete.

#### `/eval --baseline <version>`

```bash
/eval --baseline v0.1.0
```

Capture a baseline at a given version tag. Useful when backfilling baselines for hotfix releases.

#### `/eval --case <case-id>`

```bash
/eval --case feature-design-001
```

Run a single case, useful for debugging a flaky test.

#### `/eval --diff <baseline-version>`

```bash
/eval --diff v0.0.9
```

Compare current run to a specific baseline version. Show regressions, token deltas, score deltas per case.

#### `/eval --tag <tag>`

```bash
/eval --tag workflow
```

Run all cases with a specific tag. Useful for running just "design workflow" evals.

---

## 11a. Relationship to Anthropic's `skill-creator` Eval Mode (Round 4 P1)

Anthropic ships a `skill-creator` plugin (available as `anthropic-skills:skill-creator`) with built-in eval capability covering Create / Eval / Improve / Benchmark modes. Their focus: **per-skill description optimization** (description tuning, A/B activation tests, blind comparator on description variants).

Our eval framework focuses on a **different scope: workflow-level behavioral testing** (executor + judge + blind-comparator + baseline tracking + faithfulness + token budget reconciliation). The two are complementary:

| Concern | Owner |
|---|---|
| Skill description activation precision | Anthropic skill-creator Eval mode |
| Workflow behavioral correctness | Our `/eval` framework |
| Baseline regression tracking | Our `/eval --baseline` |
| Judge calibration | Our `/plugin-doctor --calibrate-judge` |
| A/B description variants | (Phase 3+) delegate to skill-creator |

**Phase 3+ integration plan:** when we want to optimize a specific skill's description, invoke skill-creator's Eval mode rather than reinventing description-optimization logic in our framework. Our eval framework remains the authoritative source for workflow-level metrics; skill-creator handles the orthogonal description-tuning concern.

---

## 12. Future Work (Not v0.1)

### A/B Description Optimization (Phase 3)

Once we ship v0.1, leverage the skill-lift data to auto-optimize skill descriptions. The `/skill-optimizer` skill will:
1. Load top-3 cases where blind-comparator lift is highest (skill is most valuable).
2. Load current skill description.
3. Suggest 5 variants of the description that emphasize different use cases.
4. A/B-test variants via eval cases.
5. Recommend the variant with highest activation precision + lift.

This is the "Skills 2.0" pattern from Anthropic's `skill-creator` plugin.

### Prompt-Level Diff Testing

Compare two versions of a skill prompt (e.g., feature-design prompt v1 vs. v2) against the same eval cases. Measure which version scores higher. Useful for iterating on skill quality without changing the skill name.

### Agent-Level Evals (Separate from Skill Evals)

Workflows with orchestrator agents (feature-design-lead, security-engineer, etc.) will eventually have separate eval cases targeting agent behavior: subagent delegation patterns, memory write correctness, failure recovery, etc.

### `prompt:` Hook Type Deployment

Current eval-judge implementation wraps an LLM call in Python. Once Claude Code v0.2+ ships with native `prompt:` hook support, replace the Python wrapper with a declarative hook that loads the rubric and invokes the judge inline. Saves ~200 lines of boilerplate.

### Live Judge Fine-Tuning (Deferred Indefinitely)

Do not attempt. Cost is prohibitive for the value. Better to manually refactor rubrics and invest in better calibration reference data.

---

## 13. Appendix: Example Eval Run Output

### Tier 1 Output (no LLM calls)

```
Eval Tier 1: Linters
====================

✓ Frontmatter validation: 42 SKILL.md files, all valid
✓ Agent fields validation: 22 agents, zero forbidden fields
✓ Secret scan: 0 hardcoded secrets found
✓ Hook executability: 7 hooks, all +x
✓ Memory commit-list enforcement: 0 violations

Tier 1 Status: PASS (100%)
Duration: 3.2s
```

### Tier 2 Output (sampled LLM calls)

```
Eval Tier 2: Smoke Tests (Sampled)
==================================

Skill Activation Precision
  feature-design: 18/20 cases activated (90%)
  develop: 19/20 cases activated (95%)
  bugfix: 17/20 cases activated (85%)
  plan: 20/20 cases activated (100%)
  release: 16/20 cases activated (80%)
  code-review: 19/20 cases activated (95%)
  plugin-doctor: 20/20 cases activated (100%)
  ralph: 18/20 cases activated (90%)
  memory-init: 20/20 cases activated (100%)
  humanizer: 19/20 cases activated (95%)
  ─────────────────────────────────────
  Overall: 186/200 (93%)  ✓ Threshold: ≥80%

Adversarial False Positives
  feature-design + wrong-domain prompt: 1/20 false-positives (5%)
  humanizer + math-problem prompt: 0/20 false-positives (0%)
  ─────────────────────────────────────
  Overall: 1/40 (2.5%)  ✓ Threshold: ≤5%

Token Usage
  Executor: 47,000
  Judge: 2,100
  Blind-comparator: 800
  Total: 49,900  ✓ Soft: 50K, Hard: 150K

Tier 2 Status: PASS
Duration: 12m 34s
```

### Tier 3 Output (Full Suite, Release Gate)

```
Eval Tier 3: Behavioral (Release Gate)
======================================

Rubric Scores
  feature-design.md       [4.3 avg] ✓ (5/5 cases ≥3.0, 0 regressions)
  develop.md              [4.1 avg] ✓
  bugfix.md               [4.2 avg] ✓
  refactor.md             [3.9 avg] ✓
  migrate.md              [4.0 avg] ✓
  spike.md                [3.8 avg] ✓ (borderline; acceptable)
  security-audit.md       [4.1 avg] ✓
  docs-pack.md            [4.2 avg] ✓
  env-analyze.md          [3.7 avg] ⚠ (one case 2.9, needs re-eval)
  ai-skills-init.md       [4.4 avg] ✓
  ─────────────────────────────────────
  Overall: 4.07 avg  ✓ Threshold: ≥4.0

Regression Analysis (vs. v0.0.9 baseline)
  feature-design-001: 4.6 → 4.5 (−0.1) ✓
  feature-design-002: 4.2 → 4.1 (−0.1) ✓
  develop-001:        4.3 → 4.2 (−0.1) ✓
  [... all cases within ±0.5 threshold ...]
  ─────────────────────────────────────
  No regressions detected ✓

Judge Calibration
  feature-design.md:      Spearman 0.81 ✓
  develop.md:             Spearman 0.78 ✓
  security-audit.md:      Spearman 0.64 ⚠ (upgrade to Sonnet?)
  [... all rubrics ≥0.7 threshold, one at risk ...]
  
Token Usage
  Executor: 420,000
  Judges: 65,000
  Blind-comparators: 12,000
  Calibration: 3,500
  Total: 500,500  ✓ Soft: 500K, Hard: 1.5M

Release Gate Status: PASS
  ✓ All rubrics ≥4.0 (min 3.8)
  ✓ No cases <3.0
  ✓ No regressions >0.5
  ✓ Tokens within budget
  ⚠ One judge under-calibrated; recommend Sonnet upgrade in v0.1.1

Duration: 2h 47m

Release APPROVED for v0.1.0
```

---

## References

- Plan §1.6 — Eval framework overview
- Corrections P12 — Eval case schema + blind-comparator mechanism
- Plan §3.6 — Three-tier model (referenced throughout)
- Plan §7a, Q4, Q5 — Token budgets and RALF caps
- Humanizer rule (`rules/humanize-content.md`)
- GEO-content rule (`rules/geo-content.md`)
- Memory-discipline rule (Phase 3: `03-MEMORY-ARCHITECTURE.md`)
- Team-protocols skill (workflow handoff format)
