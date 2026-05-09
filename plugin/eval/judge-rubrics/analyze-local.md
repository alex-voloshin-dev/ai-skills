# Analyze-Local Rubric

## Overview

Evaluates `/analyze-local` output — diagnostic for the local Docker environment (compose stack, single containers, local dev). Six dimensions × five levels. Distinct from `/analyze-prod` (production) and `/env-analyze` (broader env scope including K8s + CI).

## Dimensions

### Dimension 1: Docker Command Coverage
Used the right Docker primitives: `docker ps`, `docker logs`, `docker stats`, `docker inspect`, `docker compose ps/logs`, `docker events`.

- **Level 1:** Single command (e.g., `docker ps` only); incomplete picture
- **Level 2:** Two or three commands; gaps in evidence chain
- **Level 3:** Most relevant commands run; output cited
- **Level 4:** Full command set + output cited verbatim where it matters
- **Level 5:** All of L4 + cross-checks (e.g., `docker stats` confirms what `inspect` says about resource limits)

### Dimension 2: Issue Identification
Flagged real issues (not log noise / benign warnings); used `<common_issues>` patterns where applicable (port conflict, image-pull, healthcheck miss, OOM).

- **Level 1:** Reported noise as issues OR missed obvious issues
- **Level 2:** Mix of real issues and false positives
- **Level 3:** Real issues flagged; some noise still surfaced
- **Level 4:** Only real issues flagged + dismissed noise with reason
- **Level 5:** All of L4 + matched issue to a `<common_issues>` pattern by name

### Dimension 3: USE Method Application
Applied USE (Utilization / Saturation / Errors) for resource analysis where relevant.

- **Level 1:** No resource view, or unstructured resource numbers
- **Level 2:** Resource numbers shown without USE framing
- **Level 3:** USE method named; partially applied (one or two of U/S/E)
- **Level 4:** USE applied across all three axes for each suspect container
- **Level 5:** All of L4 + thresholds cited (e.g., "saturation > 80% over 5m = warn")

### Dimension 4: Healthcheck Awareness
Checked `--format='{{json .State.Health}}'`, OOMKilled flag, restart count, exit code, last-N seconds since last health probe.

- **Level 1:** No health-state check
- **Level 2:** `docker ps` health column only
- **Level 3:** Health JSON inspected; one of {OOMKilled, restarts, exit code} examined
- **Level 4:** Full state check: health JSON + OOMKilled + restart count + exit code
- **Level 5:** All of L4 + correlated state with the timestamps of the relevant log lines

### Dimension 5: Boundary
Escalated to `/env-analyze` for K8s/CI scope; escalated to `/analyze-prod` for any non-local cluster; did NOT touch production.

- **Level 1:** Touched non-local resources (kubectl against non-local cluster, prod creds, etc.)
- **Level 2:** Stayed local but used kubectl-style framing for a Docker problem
- **Level 3:** Stayed in scope; did not name the right escalation skill
- **Level 4:** Stayed in scope + named `/env-analyze` or `/analyze-prod` for out-of-scope branches
- **Level 5:** All of L4 + drafted the handoff payload (what context to pass to the next skill)

### Dimension 6: Output Clarity
Structured findings + per-issue remediation (commands, expected outcome, reversibility note).

- **Level 1:** No structure; "just restart it"
- **Level 2:** Findings listed; remediation vague
- **Level 3:** Findings + remediation commands; effects unclear
- **Level 4:** Findings + commands + side effects + reversibility per action
- **Level 5:** All of L4 + post-action verification command per remediation

## Scoring Logic

- **Aggregate:** average of D1–D6
- **Pass threshold:** 4.0
- **Judge model:** Haiku default; Sonnet if remediation includes destructive actions

## Anti-Patterns (Auto-Fail)

- Touched a non-local cluster (kubectl against staging/prod)
- Recommended `docker system prune -af --volumes` without confirming volume safety
- "Just restart the container" with no diagnosis
- Reported a container that does not exist (faithfulness violation)
- Used kubectl framing for a Docker compose problem (wrong tool boundary)

## Calibration Reference

- **Known-good:** `plugin/eval/calibration/analyze-local/good/*`
- **Known-bad:** `plugin/eval/calibration/analyze-local/bad/*`
