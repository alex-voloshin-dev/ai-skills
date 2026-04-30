# Role Selection Table

Match affected subproject to developer specialization. The Lead reads the task plan or bug report, determines which subproject each task belongs to, and assigns it to the Developer with the matching role.

## Subproject → Developer Mapping

Detect each subproject's tech stack from its `CLAUDE.md` or `AGENTS.md` and map to the appropriate developer role:

| Stack signal in CLAUDE.md / AGENTS.md | Developer role | subagent_type |
|---|---|---|
| React, Next.js, Vue, Angular, frontend | Frontend Developer | frontend-engineer |
| Spring Boot, Java, Kotlin backend | Java Developer | java-engineer |
| FastAPI, Django, Flask, Python backend | Python Developer | python-engineer |
| Node.js, Express, NestJS, TypeScript backend | Node.js Developer | software-engineer |
| Helm, Terraform, Pulumi, Kubernetes, IaC | DevOps Engineer | devops-engineer |
| SQL migrations, database schemas, stored procedures | DB Engineer | db-engineer |
| ML training, model pipelines, PyTorch, scikit-learn | ML Engineer | ml-engineer |
| LLM, RAG, agents, prompt systems | ML Engineer + consult `prompt-engineer` agent | ml-engineer |
| React Native, Flutter, Swift, Kotlin mobile | Mobile Developer | mobile-engineer |
| SRE, monitoring, alerting, SLOs | SRE Engineer | sre-engineer |
| ETL/ELT, Spark, dbt, Airflow, data pipelines | Data Engineer | data-engineer |
| Cloud architecture, landing zones, networking, multi-cloud | Cloud Architect | cloud-architect |
| GitHub Actions, CI/CD architecture, deployment strategy | DevOps Architect | devops-architect |

If a subproject does not match any pattern, fall back to `software-engineer`.

## subagent_type Resolution

`subagent_type` MUST match a plugin-shipped agent name in `plugin/agents/<name>.md` OR a built-in Claude Code agent (`Explore`, `Plan`, `general-purpose`). The 26 plugin-shipped agents are:

- 22 normalized: `cloud-architect`, `content-designer`, `content-writer`, `data-engineer`, `db-engineer`, `devops-architect`, `devops-engineer`, `frontend-engineer`, `java-engineer`, `marketing-strategist`, `ml-engineer`, `mobile-engineer`, `product-manager`, `prompt-engineer`, `python-engineer`, `qa-engineer`, `seo-engineer`, `software-engineer`, `solution-architect`, `sre-engineer`, `system-architect`, `ui-ux-designer`
- 4 new (B5): `security-engineer`, `feature-design-lead`, `eval-judge`, `memory-curator`

Spawn payload `subagent_role` field matches one of these names exactly.

## Spawning Rules

- If the work affects a single subproject — spawn ONE Developer with the matching role
- If the work spans multiple subprojects — spawn one Developer per affected stack
- Multiple Developers MUST NOT edit files concurrently — they take turns, coordinated by the Lead per `subagent-isolation.md` Sequential Code-Modification Gate
- Each Developer only edits files within its assigned subproject(s)
- Read each subproject's `AGENTS.md` and `CLAUDE.md` before starting work

## Bounded Recursion (per subagent-isolation.md)

Only `feature-design-lead` agent has `tools: Task` (the spawn primitive). All other plugin-shipped agents — including those mapped above as Developers/Reviewers/QA — explicitly DO NOT have Task in their tools list. They cannot spawn further subagents. This bounds recursion at depth 2: Lead (main thread) → spawned Developer/Reviewer/QA. No deeper. If the Lead needs to delegate from a Developer, that Developer returns `status: needs_clarification` instead.
