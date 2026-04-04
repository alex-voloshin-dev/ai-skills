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
| React Native, Flutter, Swift, Kotlin mobile | Mobile Developer | mobile-engineer |
| SRE, monitoring, alerting, SLOs | SRE Engineer | sre-engineer |

If a subproject does not match any pattern, fall back to `software-engineer`.

## Spawning Rules

- If the work affects a single subproject — spawn ONE Developer with the matching role
- If the work spans multiple subprojects — spawn one Developer per affected stack
- Multiple Developers MUST NOT edit files concurrently — they take turns, coordinated by the Lead
- Each Developer only edits files within its assigned subproject(s)
- Read each subproject's `AGENTS.md` and `CLAUDE.md` before starting work
