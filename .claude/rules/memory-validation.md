---
description: Validation rules for persisted memory, scope isolation, conflict resolution, and sensitive data handling.
---

# Memory Validation Reference

Use this reference for systems or assets that store persistent memory.

## Required Fields

Every persisted memory entry should record:

- source
- confidence
- created_at
- last_confirmed_at
- scope

## Resolution Rules

Resolve conflicts in this order:

1. user-stated over inferred unless superseded
2. higher confidence when the gap is material
3. more recently confirmed data
4. explicit user confirmation when ambiguity remains

## Never Store

- secrets or credentials
- raw sensitive user data without consent
- noisy raw tool dumps when a summary plus pointer is enough

## Isolation

- scope memory to the right tenant, project, or workspace
- enforce scope in code, not only in prompts
