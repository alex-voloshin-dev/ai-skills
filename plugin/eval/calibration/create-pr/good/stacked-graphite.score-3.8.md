# Stacked PR Created — feat(search): typeahead ranking (3 of 4)

> Forge: GitHub via Graphite
> Stack tool detected: `gt` (Graphite) — `.graphite_config` present in repo root
> Branch: `av/search-typeahead-ranking` → parent `av/search-typeahead-index`

## Stack-tool routing

`gh pr create` would orphan this branch from the stack. Routed to `gt submit --no-interactive` instead.

```
$ gt submit --no-interactive --update-only
✓ Submitted: av/search-typeahead-ranking
  Parent: av/search-typeahead-index (#4209)
  Children: av/search-typeahead-cache (#4211 — needs rebase after this merges)
```

## PR metadata

- Number: #4210
- Title: `feat(search): rank typeahead results by recency × match-quality`
- Parent PR: #4209 (av/search-typeahead-index) — must merge first
- Children: #4211 (downstream; gt will auto-rebase on merge of this one)

## Body

### Summary
Third PR in the typeahead stack. Adds a hybrid ranker combining recency decay and match-quality score. Read after #4209 lands.

### Stack context
```
[#4208] av/search-base                        (merged)
[#4209] av/search-typeahead-index             (in review)
[#4210] av/search-typeahead-ranking          ← this PR
[#4211] av/search-typeahead-cache             (waiting for parent)
```

### Changes
- `pkg/search/ranker.go` — new `HybridRanker`
- `pkg/search/ranker_test.go` — 8 ranking scenarios

### Test plan
- [x] `go test ./pkg/search/... -run Ranker` — 8/8 pass
- [x] Benchmark: `go test -bench BenchmarkRanker` — 142 ns/op (within 200 ns budget)

### Reviewers
@acme/search (per CODEOWNERS for `pkg/search/**`)

## Branch hygiene

- Not on `main`
- Working tree clean
- Rebased onto `av/search-typeahead-index` HEAD

## Notes for reviewer

After this merges, `gt restack` on #4211 picks up new parent SHA automatically.
