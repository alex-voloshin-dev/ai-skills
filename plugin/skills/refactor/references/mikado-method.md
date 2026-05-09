# Mikado Method (Reference)

A technique for **large structural refactors** by Ola Ellnestam and Daniel Brolund (*The Mikado Method*, Manning 2014). Use it when the goal you want is blocked by other refactorings you didn't expect.

## When to Apply

Reach for Mikado when **any** of the following is true:

- The refactor goal touches **>5 files**.
- The change crosses **module / package / service boundaries**.
- A naive attempt at the goal causes a **cascade of compile or test failures** in unrelated files.
- The goal is itself blocked by **prerequisite refactorings** that aren't yet in scope.

Below that bar, use a single named refactoring from `references/fowler-catalogue.md` instead — Mikado overhead isn't worth it for a 1–2 file change.

## Core Idea

> Try the goal directly → discover what breaks → **revert** → log the dependency in a graph → tackle the dependency first → repeat.

You never keep partial, broken code on the branch. You always commit on a green leaf. The graph is your map: leaves are work you can do today; the root is the original goal.

## Workflow

1. **State the goal** at the center (root) of a Mikado graph. Plain English: *"Extract `OrderProcessor` into shared library."*
2. **Naively attempt** the goal — make the smallest set of edits that would, in a perfect world, achieve it.
3. **Build & test.** If everything is green, congratulations — commit. (Rare for a goal worth Mikado.)
4. **If broken: revert all changes** (`git restore .` / `git stash`). Do not try to "just fix the errors" — that's how partial-refactor branches die.
5. **Log every dependency** that needs to change first as a child node in the graph. Each child is itself a smaller refactor goal.
6. **Pick one leaf-level dependency** (one that doesn't itself depend on something else yet) and recursively apply the same procedure.
7. **Working from leaves inward**, execute one prerequisite, verify with the test suite, **commit on green**.
8. Eventually the original goal becomes a single small change — execute it as the final commit.

## Concrete Example

**Goal:** Extract `OrderProcessor` into a shared library used by both `web-checkout` and `admin-tools` services.

Naive attempt: copy `OrderProcessor.java` into a new `commons-orders/` module and update imports. Build fails. Tests fail. **Revert.**

Mikado graph after the failed attempt:

```
                    [Extract OrderProcessor → commons-orders]
                                    |
        +---------+---------+--------+--------+--------+--------+
        |         |         |                 |        |        |
   [Move      [Decouple  [Replace        [Externalize [Remove   [Split
    Money      from      static          config       Spring    OrderProcessor
    type]     EmailSvc] logger w/ DI]   to env]      @Auto-    tests by
                                                      wired]    transport]
```

Each leaf is a small, independently shippable refactor:

1. **Move `Money` type** to `commons-money` — uses Move Function / Move Field.
2. **Decouple from `EmailService`** — Replace direct call with a published event (Introduce Special Case for the no-op variant in tests).
3. **Replace `static Logger.getLogger()` with constructor injection** — Encapsulate Variable + Change Function Declaration.
4. **Externalize config to env vars** — Replace Magic Number with Symbolic Constant, then read constant from env.
5. **Remove Spring `@Autowired` field injection** in favor of constructor params — Change Function Declaration.
6. **Split test class** by transport (HTTP vs message queue) — Move Function + Extract Function.

Execute leaves bottom-up. Each one ends with a green build and a commit. After all six prerequisites are merged, the original goal — copying `OrderProcessor` into `commons-orders` — is a 20-line PR.

## Anti-Patterns

- **Don't keep half-done refactoring on the branch.** Partial structural change rots fast and blocks teammates. ALWAYS revert and log the dependency in the graph.
- **Don't skip the revert** by "just fixing one more error." That's how a 2-day refactor turns into a 3-week branch with 400 conflicting files.
- **Don't commit before green.** A commit is a contract: this state of the codebase builds and passes tests. Mikado leaves are only useful if they hold.
- **Don't let the graph live in your head.** Write it down — `MIKADO.md` in the working branch, or a whiteboard photo committed under `docs/refactors/`. The graph is the artifact.
- **Don't tackle non-leaf nodes first.** A node that still has children isn't ready; doing it now means another revert.

## Automated Equivalent (git-based)

A lightweight version of Mikado without a formal graph:

```bash
# 1. Attempt the goal naively
git checkout -b refactor/extract-order-processor
# ... edits ...

# 2. Build + test fails. Stash, don't commit.
git stash push -m "naive: extract OrderProcessor — failed because Money is internal"

# 3. Tackle the prerequisite that surfaced
git checkout -b refactor/move-money-to-commons
# ... edits ...
# build green → commit + merge

# 4. Return to the goal branch, pop the stash, retry
git checkout refactor/extract-order-processor
git stash pop
# ... discover next prerequisite, repeat ...
```

Each branch corresponds to one node in the graph. Branches merge to `main` only when their leaf is fully done and verified.

## Output Artifact

When applying Mikado in a `/refactor` run, write the graph to `<repo>/.ai-assets-memory/refactor/<run-id>/MIKADO.md` so the team-lead can resume across sessions and the reviewer can see the dependency reasoning.
