# Evidence Hierarchy for Spike Investigations

Every quantitative claim in a spike report must cite its source level. Higher levels carry more weight; lower levels require explicit caveats. This hierarchy is the input to the "Confidence" axis in `decision-frameworks.md`.

## The Hierarchy (highest to lowest weight)

1. **Production benchmarks from your own system** — measured under realistic load, your stack, your data, your network topology. Cannot be argued away. Highest possible weight.
2. **Public benchmarks from an authoritative source** — cloud provider docs (e.g., the AWS DynamoDB throughput page), framework author benchmark suites (e.g., Node.js, Postgres, Redis official perf pages). Caveat: validate that the benchmark scenario matches yours (workload shape, data size, hardware class).
3. **Independent third-party benchmarks** — TechEmpower, Brendan Gregg's measurements, academic papers with reproducible methodology and published code. High weight when methodology is transparent.
4. **Vendor whitepapers** — discount for marketing bias; verify load-bearing claims against level 2 or 3 before relying on them.
5. **Conference talks and engineering blog posts** — case studies with real-world numbers but limited reproducibility; anecdotal but grounded.
6. **Stack Overflow, Reddit, blog comments, forum threads** — directional only; never the load-bearing reference for a recommendation.
7. **LLM speculation or training-data recall** — needs verification against a primary source. If an LLM is the only source for a claim, mark the recommendation as **low confidence — verify with one of levels 1–5 before committing**.

## Per-Claim Citation Requirement

For every quantitative claim in the spike report (numbers, percentages, throughput, latency, cost, memory, scale limits), cite the source level (1–7) and link to the source.

- Levels 1–4: claim stands as-is.
- Level 5: claim stands but flag the case study's context (was it your scale? your workload?).
- Level 6–7: prepend "low confidence" caveat. The recommendation cannot rest on these alone.

Format suggestion in the spike report:

> "DynamoDB sustains 40k writes/sec per partition [level 2: AWS docs, link]."
> "TechEmpower puts framework X 3x ahead of framework Y on JSON serialization [level 3: TechEmpower Round 22]."
> "An engineer on Reddit reports 200ms p99 with this config [level 6, directional only]."

## Reproducibility Check

Any benchmark claim — your own or cited — should be re-runnable. Capture in the spike artifacts:

- Exact commands used (or link to a reproducible script).
- Hardware / VM class.
- Dataset size and shape.
- Concurrency or load pattern.
- Version pins (library, runtime, OS).

If a third-party benchmark does not publish enough to reproduce, downgrade its level by one.

## Common Evidence Pitfalls

- **"Synthetic benchmark != production behavior."** Synthetic loads miss tail latency, cold caches, GC pauses, network jitter, neighbor effects. Always validate against level 1 if possible before committing.
- **"X is faster than Y" without context.** What scale? What data shape? What hardware? A 3x advantage at 10 RPS may invert at 10k RPS.
- **"Industry leaders use X."** A case study without your-context comparison is a level-5 anecdote, not a recommendation. "Netflix uses Cassandra" tells you nothing about whether you should.
- **"LLM said so."** Never enough on its own. Useful for hypothesis generation, never for the final recommendation. Always trace back to a primary source.
- **Cherry-picked benchmark scenarios.** Vendor whitepapers often pick the scenario that flatters their product. Read the methodology section before trusting the headline number.

## Anti-Pattern

A spike report whose load-bearing citations are all level 6–7 (Reddit / HN / forum threads / LLM recall) is not a finished spike. Restart with proper sources, or downgrade the recommendation to `needs more spike before commit` and list the gaps.

## Wiring to the Decision Lens

The "Confidence" axis in the decision recommendation lens (`decision-frameworks.md`) maps directly to source levels:

- Levels 1–4 → **high confidence**.
- Level 5 → **medium confidence**.
- Levels 6–7 → **low confidence** (recommendation cannot be `go-one-way` on these alone).
