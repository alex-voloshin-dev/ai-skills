---
trigger: model_decision
description: Failure recovery for tool loops, context loss, invalid arguments, and goal drift during Windsurf sessions.
---

# Failure Recovery

Use this recovery flow when Windsurf work starts looping, drifting, or losing constraints.

## Context Loss

1. checkpoint completed work
2. restate active constraints near the top of the context
3. continue from the last verified state

## Tool Loops

1. detect repeated tool calls with the same intent
2. change approach instead of retrying blindly
3. stop and report if one materially different retry also fails

## Goal Drift

1. compare current actions against the user request
2. discard off-target work
3. resume from the last on-goal checkpoint

## Invalid Tool Arguments

1. re-read tool schema or local state
2. ground arguments in observed data
3. retry only with verified parameters

## Failed Delegation

1. isolate incorrect or partial delegated output
2. retry with a narrower request or continue locally
3. report the limitation if it affects the result
