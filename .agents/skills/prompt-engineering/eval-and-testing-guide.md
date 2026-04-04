# Prompt Eval and Testing Guide

Use this file as the overview for prompt evaluation. The detailed mechanics now live in narrower companion files so each resource stays under the repository markdown limit.

## Eval-First Rule

Never change a prompt without:

1. baseline metrics
2. a representative eval set
3. explicit graders
4. regression gates
5. success criteria

## Evaluation Flow

```text
Define metrics -> curate dataset -> choose graders -> run baseline ->
change prompt -> rerun eval -> compare against gates -> canary deploy ->
monitor -> add failures back to regression set
```

## What to Open Next

| Need | File |
|---|---|
| Build or refresh the eval dataset | `eval-datasets-and-graders.md` |
| Choose exact graders and scoring logic | `eval-datasets-and-graders.md` |
| Define rollout, rollback, and monitoring | `eval-deployment-and-monitoring.md` |
| Review regression, A/B, and canary gates | `eval-deployment-and-monitoring.md` |

## Minimum Shipping Checklist

- baseline recorded
- dataset covers typical, edge, adversarial, and regression cases
- schema or output compliance is measured
- safety regressions have zero tolerance
- rollout plan and rollback trigger exist
- production monitoring is version-aware
