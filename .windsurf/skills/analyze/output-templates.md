# Analysis Output Templates

Use these templates to keep analytical outputs consistent and scannable.

## Universal Shape

Every analysis should contain:

1. Executive summary
2. Context
3. Analysis
4. Findings
5. Recommendations
6. Risks and limitations

## Template: Technical Assessment

```markdown
# [Subject] Technical Assessment

## Executive Summary
[2-4 sentences: overall answer and primary recommendation]

## Context
- Situation: [current state]
- Question: [what this analysis answers]

## Analysis
### [Dimension 1]
- Finding: [what was observed]
- Evidence: [data, source, file, metric]
- Implication: [why it matters]

### [Dimension 2]
- Finding: ...

## Findings
1. [Critical or high-signal finding]
2. [Next finding]

## Recommendations
1. [Immediate action]
2. [Short-term action]
3. [Longer-term action]

## Risks and Limitations
- [Assumption, missing data, or scope boundary]
```

## Template: Comparison

```markdown
# [Subject] Comparison Analysis

## Executive Summary
[Recommended option and why]

## Context
- Options: [list]
- Decision criteria: [list]

## Evaluation Matrix
| Criterion | Weight | Option A | Option B |
|---|---|---|---|
| [criterion] | [%] | [score] | [score] |

## Findings
1. [Finding]
2. [Finding]

## Recommendation
[Selected option, tradeoffs, conditions]

## Risks and Limitations
- [Sensitivity or missing information]
```

## Template: Root Cause Analysis

```markdown
# [Subject] Root Cause Analysis

## Executive Summary
- Root cause: [one sentence]
- Impact: [scope]
- Recommended fix: [one sentence]

## Problem Statement
- What: [problem]
- When: [timeline]
- Where: [systems or users affected]

## Evidence
| # | Evidence | Source | Relevance |
|---|---|---|---|
| E1 | [finding] | [source] | [why it matters] |

## Analysis
1. Why [symptom]? -> [cause]
2. Why [cause]? -> [deeper cause]

## Recommendations
1. [Mitigation]
2. [Durable fix]
3. [Prevention]

## Risks and Limitations
- [uncertainty]
```
