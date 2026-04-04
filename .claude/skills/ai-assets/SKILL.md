---
name: ai-assets
description: Create, modify, validate, and analyze Claude Code AI assets (rules, workflows, skills, hooks, CLAUDE.md) with prompt engineering discipline and dependency chain awareness
---

# AI Assets

Guides creation, modification, and validation of Claude Code AI assets. Every asset is a prompt for an LLM — apply prompt engineering rigor throughout.

**Apply `Agent(prompt-engineer)` role for all steps below.**

## 1. Determine Operation and Scope

Clarify with the user:

- **Operation**: `create` | `modify` | `validate` | `analyze`
- **Asset type**: `rule` | `workflow` | `skill` | `hook` | `agents-md`
- **Target**: file path or asset name

If the user's intent is ambiguous, ask before proceeding.

## 2. Gather Context

Read and internalize before making any changes:

1. **Target asset** (if exists — for modify/validate/analyze)
2. **Vendor specs**: `framework-summary.md` — Section 2.x matching the asset type. This is the authoritative source for Claude Code capabilities, formats, and constraints
3. **Authoring standards**: `rules/global-rules.md` — language, file size limits, cross-reference rules
4. **Project conventions**: `CLAUDE.md` — naming, frontmatter, source management, interconnection patterns
5. **Existing assets of the same type** — scan the target directory to understand tone, structure, and naming patterns already in use
6. **Context engineering guide**: `context-engineering` skill — context stack model, production checklists, reference templates. Required reading for AI-facing assets

## 3. Map Dependency Chain

Search the entire asset tree for references to/from the target. Build a dependency map:

```
[target asset]
├─ OUT (this asset references):
│  ├─ /workflow-name  → file path [OK | MISSING]
│  ├─ @skill-name    → file path [OK | MISSING]
│  └─ rule-name      → file path [OK | MISSING]
├─ IN (referenced by):
│  ├─ asset-a.md (line N)
│  └─ asset-b.md (step N)
└─ HOOKS (enforced by):
   └─ script.py → hook event
```

**Search patterns**: `/asset-name`, `@asset-name`, `../type/path.md`, prose mentions in integration sections.

**Flag issues**:
- **Broken refs**: outgoing reference target doesn't exist
- **Orphaned**: zero incoming references (nothing calls or mentions this asset)
- **Missing links**: asset logically belongs in a chain but isn't connected
- **Circular deps**: A → B → A (acceptable for rules↔workflows, flag for review otherwise)

For `analyze` operations — present the full map and stop here. For other operations — use the map to inform subsequent steps.

## 4. Companion Asset Analysis

Before authoring, evaluate whether the target asset needs **companion assets** to be effective:

- **Rule** that defines a multi-step procedure → extract to a **skill** with checklists as resource files
- **Rule** that needs automated enforcement → propose a **hook** script
- **Workflow** with reusable sub-sequences → extract **sub-workflows** (`/sub-workflow`)
- **Workflow** that bundles complex knowledge → extract a **skill** for the knowledge, reference via `@skill-name`
- **Skill** that operationalizes a rule → verify the **rule** exists and cross-references the skill
- **Any asset** approaching 12K chars → split: offload detail to skill resources or sub-workflows

If companion assets are needed, create them as part of the same operation. Apply this entire workflow to each companion asset recursively (steps 2–8).

## 5. Author or Edit the Asset

Apply the asset-type spec from `framework-summary.md` Section 2.x:

<rule_spec>
- **Frontmatter**: `trigger` ((auto-loaded) | (agent) | `glob` | `manual`), `description`
- **`description`** is the activation signal for (agent) — write it as a keyword-rich, specific summary. Too broad = false positives. Too narrow = missed activations
- Trigger mode: (auto-loaded) for foundational constraints; (agent) for contextual guidance; `glob` for file-type-specific; `manual` for on-demand roles/expertise
- Structure: imperative instructions, bullet points, numbered lists, XML tags for sections
- Max 12,000 chars
</rule_spec>

<workflow_spec>
- **Frontmatter**: `description`
- Numbered steps — each step is one concrete action with a clear completion criterion
- Compose with `/sub-workflow` to avoid duplication across workflows
- Include decision points (if/then) for branching logic
- Max 12,000 chars
</workflow_spec>

<skill_spec>
- **Folder**: `skill-name/SKILL.md` + resource files
- **Frontmatter**: `name`, `description`
- `description` drives progressive disclosure — optimize for automatic activation by Claude Code
- Offload checklists, templates, guides to resource files (no size limit on resources)
- Max 12,000 chars for SKILL.md only
</skill_spec>

<hook_spec>
- **Config**: JSON with hook event name, command, working directory
- **Script**: Python 3; stdin JSON; exit 0 (pass) or 2 (block)
- 11 events: `pre/PostToolUse (Read)`, `pre/PostToolUse (Write|Edit)`, `pre/PostToolUse (Bash)`, `pre/PostToolUse`, `UserPromptSubmit`, `Stop`, `WorktreeCreate`
- Merge order: System → User → Workspace (all execute)
</hook_spec>

<agents_md_spec>
- No frontmatter — auto-scoped by directory placement
- Root = always on; subdirectory = scoped to that dir tree
- Focus: what this directory does, which rules/workflows/skills apply
- Be specific, avoid redundancy with parent CLAUDE.md
</agents_md_spec>

### Role Hierarchy and Routing

Design role rules for composable specialization via Claude Code's agent/skill system:

- **Layer 1 — Base role** ((agent)): Universal principles, reasoning protocol, hard rules. Example: `software-engineer.role.md`
- **Layer 2 — Specialization** ((agent) or `glob`): Stack-specific patterns. (agent) for project context matching; `glob` for file-type binding
- **Layer 3 — Explicit override** (`manual`): User forces via `@role-name`

**Routing**: CLAUDE.md declares tech stack → (agent) roles with matching `description` keywords activate automatically → `glob` activates on file patterns → multiple roles compose (base + specialization)

**Composability rules**:
- Base MUST NOT duplicate specializations; specializations MUST NOT duplicate base
- Each role's `description` must clearly state scope to avoid activation overlap

## 6. Prompt Engineering Review

**Every asset is a prompt for an LLM.** Apply `Agent(prompt-engineer)` Reasoning Protocol to evaluate each asset:

1. **Assess** — identify the prompt surface: what will Claude Code read and how will it shape behavior?
2. **Diagnose** — what could go wrong? (wrong activation, vague instructions, conflicting rules, token waste, missed edge cases)
3. **Design review** — verify the asset follows prompt engineering principles below
4. **Eval** — define ≥1 scenario proving the asset works as intended + ≥1 scenario where it should NOT activate

### Universal Checks (all asset types)

1. **Instruction clarity**: imperative, unambiguous. No hedging ("try to", "consider") — use "do X", "never Y", "always Z"
2. **Structure**: sections separated via headings, XML tags, bullet lists. Instructions never buried in prose
3. **Token efficiency**: every token earns its place. Remove filler, redundancy, obvious statements
4. **Instruction hierarchy**: system constraints > developer guidelines > user preferences. Explicit priority on conflicts
5. **Security**: no secrets, PII, API keys. Instructions separated from data. No injection vectors
6. **Conflict check**: no contradictions with other active assets (rules, CLAUDE.md, other workflows)

### Context Engineering Checks (all asset types)

Apply `context-engineering` skill principles — every asset is context that enters Claude Code's window:

7. **Context stack awareness**: Which context stack layer does this asset operate in? (L1: policy, L2: developer instructions, L3: tool contracts, L4: runtime state, etc.)
8. **Position effects**: Critical constraints (Hard Rules, NEVER items) placed at the beginning. Output contracts at the end. No critical info buried in the middle of long sections
9. **Layer separation**: Policy ("never do X") is separate from knowledge ("how to do Y"). No mixed sections
10. **Token budget impact**: Does this asset justify its token cost? Can any section be compressed without losing signal?
11. **Cacheable prefix**: For roles/rules — static content that rarely changes grouped to enable KV cache reuse

### Asset-Type-Specific Checks

**Rules** ((agent)):
- Does `description` contain keywords users naturally use when the rule should activate?
- Is it specific enough to avoid false positives, broad enough to not miss real cases?
- Does it differentiate clearly from other rules with similar scope?
- Are negative instructions ("do NOT", anti-patterns) sufficient to prevent wrong behavior?
- Will Claude Code consistently produce the intended behavior when this rule is active?

**Workflows**:
- Does each step have a clear completion criterion?
- Are decision points (if/then) explicit — no ambiguous branching?
- Could Claude Code execute this workflow autonomously with minimal user input?
- Are sub-workflow calls (`/name`) and skill refs (`@name`) correct?

**Skills**:
- Does `description` trigger progressive disclosure for the right tasks only?
- Are resource files referenced and accessible?
- Is knowledge actionable (checklists, patterns) vs purely informational?

**Rules (roles)**:
- Are Hard Rules concrete and testable (not aspirational)?
- Is the role boundary clear — what is in scope vs delegated?
- Does it compose cleanly with Layer 1 base role without duplication?

## 7. Validate (mandatory on every create/modify)

**This step is non-optional.** Run the full checklist on every create or modify operation to prevent dependency corruption, broken cross-references, and size violations.

**Format**: correct frontmatter, ≤12K chars, English, naming convention per `CLAUDE.md`

**References**: all `/workflow`, `@skill`, and relative paths resolve. No absolute paths. Cross-references updated

**Prompt quality**: Step 6 checks passed, `description` activation-appropriate, no secrets/PII, behavioral test passes

**Context engineering**: maps to context stack layer, no lost-in-the-middle, policy/knowledge separated

**Dependency chain**: no broken refs, asset reachable, no collateral damage, companions validated

## 8. Finalize

1. Verify all assets (primary + companions) are saved in correct directories
2. If cross-references changed, verify all affected assets are updated
3. Present a summary to the user:
   - What was created/modified (list all assets including companions)
   - Dependency chain status (all refs OK / issues found)
   - Role routing status (for role assets: which layers are covered, CLAUDE.md tech stack alignment)
   - Validation checklist result (all passed / items requiring attention)
   - Any remaining action items
