# /spike — Time-boxed exploration with go/no-go writeup

Single-pass research workflow producing a SPIKE-REPORT with a go/no-go/needs-more-info recommendation.

## When to use

- "Can we use gRPC instead of REST?"
- "Best way to implement real-time sync?"
- "Is this library production-ready?"
- "Research: what's our path to multi-region deployment?"

## Not for

- Decisions already made → just `/plan` then `/develop`
- Open-ended exploration with no question — `/spike` requires a stated question
- Convergence on a binary success signal → use [`/ralph`](feature-design.md) (spike is exploration, not iteration)

## How to invoke

```bash
/spike "Can we use gRPC instead of REST?" --time-cap 120
/spike "Best way to implement real-time sync" --poc
/spike "Is Postgres pg_vector production-ready for our scale?" --time-cap 90
```

| Flag | Default | Effect |
|---|---|---|
| `<question>` (positional) | required | Research question |
| `--time-cap <min>` | 180 | Wall-time cap |
| `--poc` | off | Build minimal proof-of-concept code in `<repo>/spike-poc-<run-id>/` |

## What you get

- `<repo>/.ai-skills-memory/spikes/<run-id>/SPIKE-REPORT.md` — findings, pro/con, recommendation
- (optional) `<repo>/spike-poc-<run-id>/` — POC code if `--poc`
- Memory: research record to L4 for future reference

## How it works

The Lead picks a subject-matter-expert role based on the question domain (e.g., `db-engineer` for schema questions, `ml-engineer` for ML questions, `solution-architect` for architecture).

1. **Researcher** explores the question exhaustively within the time cap; gathers evidence (docs, benchmarks, examples); builds POC if `--poc`; estimates effort if go/no-go.
2. **(Optional) Reviewer** — `technical-reviewer` stress-tests findings, identifies gaps.
3. **Memory write** — research record to L4.
4. **Report + recommendation** — go / no-go / needs-more-info, with next steps.

No RALF — spike is exploration. Time-cap enforces the deadline.

## The Q4 hard rule (`.committed/decisions/`)

`.committed/decisions/<date>-<question>.md` is **always-asked-before-write**. Even if the spike concludes with a clear recommendation, the workflow asks before writing to the committed decisions directory — `.committed/` goes to git and you may want to reword the decision before committing.

## Common questions

**What if the time cap hits before research is complete?**
Researcher pauses at time-cap; produces partial report with `[INVESTIGATION INCOMPLETE]` marker and a "more investigation needed" section listing data gaps.

**What if findings are inconclusive?**
Report states inconclusive with specific data gaps; recommends a deeper spike or prototype.

**What if the POC doesn't compile?**
Report failure as a finding — the POC failure is itself a data point for go/no-go. Don't block the spike.

**Can I run multiple spikes in parallel?**
Yes — they're independent. Each writes to its own `.ai-skills-memory/spikes/<run-id>/`.

## Examples

### Tech evaluation
```bash
/spike "Can we use gRPC instead of REST?" --time-cap 120
```
db-engineer or solution-architect researches; produces benchmarks; recommends go/no-go with effort estimate.

### POC for new approach
```bash
/spike "Real-time sync via CRDTs vs Operational Transform" --poc --time-cap 240
```
ml-engineer or solution-architect builds two minimal POCs; reports trade-offs.

### Library / vendor evaluation
```bash
/spike "Is Pinecone vs Weaviate the better fit for our RAG use case?" --time-cap 90
```
ml-engineer compares against our requirements; recommends with switching cost analysis.

## Related

- [`/plan`](feature-design.md) — when you've decided what to build and need to plan it
- [`/feature-design`](feature-design.md) — when you need a full design pack from a spike's go decision
- [`/ralph`](feature-design.md) — for iteration loops with binary success signals (spike is for exploration)
- [Memory](../concepts/memory.md) — research records persist; `.committed/decisions/` always-asked
