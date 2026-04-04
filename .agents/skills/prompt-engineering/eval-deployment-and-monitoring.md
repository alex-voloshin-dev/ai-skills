# Eval Deployment and Monitoring

## Regression Gates

Before rollout:

- no regression on core quality metrics
- zero tolerance for safety regressions
- explicit thresholds for cost and latency
- documented success criteria for the primary metric

## A/B Testing

Use A/B testing for:

- major prompt rewrites
- model upgrades
- new orchestration strategies
- changes that affect production behavior materially

Protocol:

1. define a hypothesis
2. choose one primary metric
3. choose guardrail metrics
4. calculate sample size
5. run long enough to catch usage variation
6. decide only after significance and guardrail review

## Context and Pipeline Health

Track:

- context utilization
- cache-prefix ratio
- evidence density
- output-to-input ratio

These are often early-warning signals for silent prompt degradation.

## Prompt Change Deployment

Use a canary path:

1. 5% canary
2. 25% expansion
3. 100% rollout

Rollback automatically if:

- hallucination rate rises past threshold
- schema or tool-call error rate spikes
- latency or token cost drifts beyond budget
- task success rate falls below gate

## Monitoring Requirements

Trace every request with:

- prompt version
- model
- input and output tokens
- latency
- tool calls
- output

Review weekly:

- failure clusters
- newly emerging edge cases
- stale eval datasets
- regressions tied to model or corpus changes

## Incident Response

1. detect the degradation
2. isolate prompt version, model, and request category
3. roll back
4. diagnose the new failure mode
5. patch the prompt or runtime guardrail
6. add the failure to the regression set
