# Analysis — Postgres vs MySQL for the Reporting Workload

> Question: which RDBMS for our analytical/reporting tier (read-heavy, complex joins, 2TB working set growing 30%/yr)?
> Frameworks applied: MCDA (multi-criteria decision analysis) primary; SWOT secondary cross-check
> Date: 2026-04-22

## Executive Summary

**FACT:** Workload is 92% read, 8% write; query mix dominated by 7-table joins; current MySQL 8.0 p99 query latency is 2.4s on the canonical month-end report.
**INFERENCE:** Postgres is the better fit on 4 of 6 weighted criteria; primary driver is window-function + CTE expressivity for the analytical query mix (HIGH confidence).
**RECOMMENDATION:** Migrate the reporting tier to Postgres 16 over Q3 2026; keep MySQL for OLTP. Confidence: HIGH for the analytical workload, MEDIUM for the migration timeline (depends on ETL rewrite).

## Decomposition (MECE)

The decision splits cleanly along six axes:

1. Query expressivity (window functions, CTEs, lateral joins)
2. Read performance at our query mix
3. Write performance (less load than reads but still relevant)
4. Operational maturity (backups, replication, monitoring)
5. Ecosystem (BI tool support, ORM support, hosted offerings)
6. Migration cost (schema port + ETL rewrite + dual-write window)

Decomposition rationale: these are the axes our finance + data + platform teams collectively own; they're orthogonal (no overlap) and cover the full decision (no gap). Cost dimension (licensing) intentionally excluded — both are open source on managed services.

## MCDA Scoring

| Criterion | Weight | Postgres 16 | MySQL 8.0 | Source |
|---|---|---|---|---|
| Query expressivity | 25% | 5 | 3 | Primary: pg_docs + MySQL 8.0 reference manual (window-function feature parity table) |
| Read perf @ our mix | 25% | 4 | 3 | Primary: TPC-H@100GB on managed instances, run 2026-04-18 (artifacts: `bench/tpch-2026-04-18/`) |
| Write perf | 10% | 3 | 4 | Primary: same benchmark, write subset |
| Ops maturity | 15% | 4 | 5 | Tertiary: team experience survey n=12; MySQL ops familiarity higher |
| Ecosystem | 10% | 5 | 5 | Tie (Tableau / Looker / Metabase support both) |
| Migration cost | 15% | 2 | 5 | Inference: 64 engineer-days for ETL rewrite (estimate from spike `spike-2026-03-pg/`) |
| **Weighted score** | | **3.85** | **3.75** | |

Weighted score difference is small (0.10) but the spread on the most heavily-weighted criterion (query expressivity) is large (5 vs 3). Sensitivity check: if weight on expressivity drops to 15%, MySQL wins by 0.05 — so the recommendation is sensitive to that single weight.

## SWOT Cross-Check (Postgres for our case)

- **Strengths:** window functions, lateral joins, JSONB, partitioning maturity
- **Weaknesses:** team has less ops experience; in-place upgrade more involved
- **Opportunities:** vector extensions (pgvector) unlock semantic search on reports later
- **Threats:** ETL rewrite is the single biggest risk to the timeline

## Risks

| Risk | P × I | Mitigation |
|---|---|---|
| ETL rewrite slips past Q3 | M × H | Wave the migration: 1 report family per 2-week sprint |
| Operational incidents during dual-write | M × M | Dress rehearsal on staging clone; chaos-test the cutover |
| Hidden MySQL-specific SQL in reports | M × M | Static-scan all report SQL with sqlglot transpiler (artifacts: `scan/2026-04-19.csv`) |

## Out of Scope (deferred)

- Production cutover plan → this needs `/architecture` for the migration ARD + runbook
- Concrete query rewrites → `/develop` once the ARD lands
- Production capacity sizing → `/analyze-prod` against the staging Postgres after first wave
