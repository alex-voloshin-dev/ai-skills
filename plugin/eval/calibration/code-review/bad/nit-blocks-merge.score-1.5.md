# Code Review — PR #4612: Refactor logging in `OrderProcessor`

## Verdict: REQUEST_CHANGES

## Findings

The variable `log` should really be named `logger`. We use `logger` everywhere else in the codebase. This needs to be fixed before I can approve.

Also, the import of `org.slf4j.Logger` is alphabetically out of order with the other imports. That's not how we do it here.

The blank line between methods on lines 42 and 44 should be a single blank line, not two.

I'd prefer if the lambda inside `processOrder` were a method reference instead. It's just cleaner that way.

## Decision

Cannot merge. Fix the naming, sort imports, normalise the blank lines, and convert the lambda. Then ping me again.
