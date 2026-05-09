---
name: analytical-frameworks
description: Catalog of analytical frameworks for the /analyze workflow. Loaded by SKILL.md Step 2 when picking 1–3 frameworks for a given question type.
---

# Analytical Frameworks Catalog

Pick 1–3 frameworks per analysis. Each entry: when to use, key questions, output shape. Match the framework to the question; do not force-fit.

## Root-Cause / Diagnostic

### 5 Whys (Toyoda)

**When to use**: a single observable problem with a likely chain of mechanical causes (incidents, defects, process breakdowns). Best on technical / single-loop problems where causes are largely deterministic. Less useful on socio-technical or multi-causal failures.

**Key questions**:
1. What is the observed problem?
2. Why did it happen? (Why 1)
3. Why did *that* happen? (Why 2 — usually the proximate cause)
4. Continue 3–5 levels until you reach a cause whose removal prevents recurrence.

**Output**: ordered chain of causes + root cause + corrective action per level.

**Anti-pattern**: stopping at the first plausible answer; treating "human error" as a root cause (it almost never is — ask why the system allowed the error).

### Fishbone / Ishikawa Diagram

**When to use**: multi-causal problems where 5 Whys is too linear; when team needs to enumerate possibilities before testing them. Useful for incidents, quality defects, missed deadlines.

**Key questions** (categorize causes under standard branches):
- **People**: skills, training, communication, ownership
- **Process**: workflow, gates, handoffs, documentation
- **Tools**: software, infrastructure, instrumentation
- **Environment**: external dependencies, organizational pressure, market changes
- **Inputs**: data quality, requirements, materials
- **Measurement**: metrics, monitoring, feedback loops

**Output**: branching diagram (mermaid `flowchart LR` or table) with verified vs hypothesized causes.

### Causal Loop / Feedback Analysis

**When to use**: problems that *recur* despite fixes (suggests reinforcing feedback loop) or that *self-correct* unexpectedly (balancing loop). Common in SaaS metrics, team dynamics, performance regressions.

**Key questions**: Which variables reinforce each other (R loop)? Which counteract (B loop)? Where is the dominant loop's leverage point?

**Output**: causal loop diagram + identification of dominant loop + leverage point recommendation.

## Decomposition / Structuring

### MECE (Mutually Exclusive, Collectively Exhaustive)

**When to use**: any analysis that needs to break a question into parts before investigating. Foundational discipline — apply to almost every plan in Step 3 of SKILL.md.

**Key questions**: Are the categories non-overlapping? Do they cover the whole problem? Is there a residual "Other" bucket that hides important cases?

**Output**: tree or table where each leaf is investigated independently and findings re-aggregate cleanly to the root.

### Pyramid Principle / SCQA (Minto)

**When to use**: structuring the *output*, not the analysis. Applies to executive summaries, recommendations, board materials.

**Key questions**:
- **S**ituation: what is the current state the audience knows?
- **C**omplication: what changed, what's at risk, why act now?
- **Q**uestion: what decision must be made?
- **A**nswer: what is the recommendation? Supported by 3 grouped reasons, each with evidence.

**Output**: top-down argument: governing thesis → 3 supporting key points → evidence per point. Reader can stop at any level and still grasp the argument.

## Strategy / Positioning

### SWOT

**When to use**: quick first pass at a strategic situation. Best as input to deeper analysis, not as a deliverable on its own.

**Key questions**:
- **S**trengths (internal, positive)
- **W**eaknesses (internal, negative)
- **O**pportunities (external, positive)
- **T**hreats (external, negative)

**Output**: 2x2 matrix. Pair S+O (use strengths to capture opportunities), W+T (defensive priorities), W+O (build capability), S+T (mitigate). The pairings are where SWOT becomes actionable.

**Anti-pattern**: bullet-list SWOT with no pairings — purely descriptive, not strategic.

### Porter's Five Forces

**When to use**: assessing structural attractiveness of a market or competitive position. Applies before market entry, pricing decisions, M&A.

**Key questions**:
1. Threat of new entrants (barriers, switching costs, capital requirements)
2. Bargaining power of suppliers (concentration, switching cost, substitutes)
3. Bargaining power of buyers (concentration, price sensitivity, switching cost)
4. Threat of substitutes (price/performance trends, switching propensity)
5. Rivalry among existing competitors (number, growth rate, exit barriers)

**Output**: per-force assessment (high/medium/low + rationale) + overall industry attractiveness + leverage points.

### Jobs-to-be-Done (JTBD, Christensen)

**When to use**: product strategy, ICP definition, feature prioritization. When competitive positioning isn't about features but about the "job" the customer hires the product to do.

**Key questions**:
- What is the *job* (functional + emotional + social)?
- What is the *struggle* (current solution's pain points)?
- What are the *forces* — push from current solution, pull of new, anxiety, habit?
- Who else can do this job? (competitive set is broader than direct competitors.)

**Output**: job statement (`When I [situation], I want to [motivation], so I can [outcome]`) + force diagram + ICP segmentation by job.

### Wardley Mapping

**When to use**: technology / platform strategy where understanding *evolution* of components (genesis → custom-built → product → commodity) is decisive. Appropriate when the question is "build vs buy", "where to invest", "what will be commoditized".

**Key questions**: What is the user need at the top? What chain of components delivers it? Where is each component on the evolution axis? What's moving?

**Output**: Wardley map (value chain on Y, evolution stage on X) + identified strategic moves (climate, doctrine, gameplay).

## Decision-Making

### Multi-Criteria Decision Analysis (MCDA) / Weighted Scoring

**When to use**: comparing 2–N options against multiple criteria of unequal importance. Standard for technology selection, vendor evaluation, architecture decisions.

**Key questions**:
1. What are the options?
2. What are the criteria? (typically 5–10; more dilutes signal.)
3. What is each criterion's weight? (force-rank or pairwise compare; weights sum to 1.0.)
4. What is each option's score per criterion? (1–5 scale; document evidence.)
5. Compute weighted score per option. Sensitivity-test the top 2.

**Output**: criteria matrix + weighted total + top-2 sensitivity analysis ("if weight on X drops 30%, does ranking flip?") + recommendation.

**Anti-pattern**: choosing the option first and back-fitting weights — the sensitivity test exists to catch this.

### Cynefin (Snowden)

**When to use**: classifying the *kind* of problem before choosing an approach. Critical because the right method differs by domain.

**Domains** (the framework's central insight is that different domains demand different decision-making styles):
- **Clear**: cause-effect obvious. *Sense → categorize → respond*. Best practices apply.
- **Complicated**: cause-effect knowable with expertise. *Sense → analyze → respond*. Good practices apply; engage experts.
- **Complex**: cause-effect known only in retrospect. *Probe → sense → respond*. Run small safe-to-fail experiments; emergent practice.
- **Chaotic**: no cause-effect. *Act → sense → respond*. Stabilize first; novel practice.
- **Confusion** (center): you don't know which domain you're in. Break the problem apart.

**Output**: domain classification per sub-problem + chosen approach + acceptable-failure boundary if Complex/Chaotic.

### Two-Way / One-Way Doors (Bezos)

**When to use**: speed vs reversibility decisions. Match decision speed to reversibility.

**Key questions**:
- Is this decision *reversible* (two-way door — costs to reverse are bounded)?
- Or *irreversible* (one-way door — cost of being wrong is large)?

**Rule**: two-way doors should be made fast (delay is the dominant cost). One-way doors deserve slow, multi-perspective review.

**Output**: classification + decision-process matched to type ("two-way door, will commit by EOD" vs "one-way door, scheduling review with 3 stakeholders next week").

## Technical / System Assessment

### Architecture Review (C4-aligned)

**When to use**: assessing an existing system or component for fit, risk, evolution.

**Key questions** (per level):
- **Context**: who uses the system, what other systems does it interact with?
- **Container**: what are the major runtime components (apps, datastores, queues)?
- **Component**: within each container, what are the major modules and their responsibilities?
- **Code**: only when a specific module's design is in question.

**Output**: C4 diagrams (Mermaid `C4Context` / `C4Container`) + per-level findings table (component → strengths → risks → recommendations).

### Gap Analysis

**When to use**: comparing current state to target state across multiple dimensions. Common for compliance, capability, NFR (performance/scale/security/operability).

**Key questions**:
- What dimensions matter? (define before measuring — avoids cherry-picking.)
- What is the *current* state per dimension? (evidence-based, not opinion.)
- What is the *target* state per dimension? (sourced from requirements, SLOs, regulations.)
- What is the *gap*? (size, criticality, effort to close.)

**Output**: dimension × {current, target, gap, severity, owner} table + prioritized closure roadmap.

### Technical Debt Assessment

**When to use**: prioritizing remediation work. Especially before "let's do a refactor sprint" decisions.

**Key questions** (per debt item):
- What is the debt? (description + location)
- What is the *interest cost*? (slowdown, defect rate, on-call burden, hiring difficulty)
- What is the *principal*? (effort to fully repay)
- What is the *risk* of not paying? (breaking-change cost, security exposure)
- What forces a payment? (looming requirement, dependency upgrade, scale)

**Output**: register with each item scored on Interest × Principal × Risk; ranked list; clearance plan (hot — pay now, cold — accept as fixed cost).

## Risk

### Risk Matrix (Probability × Impact)

**When to use**: any analysis that produces a forward-looking recommendation. Risks are an obligatory output, not optional.

**Key questions** (per risk):
- Probability: low / medium / high (with rationale, not gut feel)
- Impact: low / medium / high (with rationale, scoped to the decision)
- Mitigation: prevent, detect, accept, transfer
- Residual probability and impact after mitigation

**Output**: 3×3 matrix + per-risk row (probability, impact, mitigation, owner, residual). Color-code top-right (high P × high I) as immediate.

### Pre-mortem (Klein)

**When to use**: before committing to a plan. Surfaces failure modes that optimistic forward-planning misses.

**Key questions**:
1. Imagine: it's 6 months from now and the plan failed catastrophically. Why?
2. List every reason without filtering.
3. Cluster reasons. For each cluster: what early signal would warn us? What pre-emptive mitigation exists?

**Output**: ranked failure-mode list + early-warning signals + mitigations woven into the plan before execution.

## Selection Heuristic

If unsure which to pick:

| Question type | First-choice frameworks |
|---|---|
| Why did X happen? | 5 Whys → Fishbone (if multi-causal) |
| What kind of problem is this? | Cynefin |
| Which option do we pick? | MCDA + Two-Way Doors classification |
| Should we enter / invest in this market? | Five Forces + JTBD |
| How does our current state compare to target? | Gap Analysis |
| Will this plan fail? | Pre-mortem + Risk Matrix |
| Where is the dominant feedback loop? | Causal Loop |
| How should I structure my answer? | SCQA / Pyramid Principle |
| Build vs buy? | Wardley Mapping |
| What part of the system is risky? | Architecture Review (C4) |
| What technical debt to repay first? | Technical Debt Assessment |

If the question doesn't match any row, default to MECE decomposition + targeted depth-first investigation.
