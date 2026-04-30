# How we cut our build time from 8 minutes to 90 seconds

Our CI build used to take eight minutes. Most of that was spent on dependency installation. Two changes brought it down to ninety seconds: caching the dependency layer in Docker, and switching from `npm install` to `npm ci`.

## The slow build

The build started a fresh container, installed Node, ran `npm install` from scratch, and then compiled. Three of these steps happened on every commit, even though the dependencies rarely changed.

We measured each step:

- Node install: 45 seconds
- `npm install`: 4 minutes 30 seconds
- TypeScript compile: 1 minute 20 seconds
- Tests: 1 minute 25 seconds

Total: 8 minutes 0 seconds.

## What changed

First, we put dependency installation in its own Docker layer. The `Dockerfile` copies `package.json` and `package-lock.json`, runs `npm ci`, and only then copies the source code. Because the package files rarely change, Docker reuses the cached layer for most builds.

Second, `npm ci` is faster than `npm install` because it skips dependency resolution and trusts the lockfile. For a CI environment, that's the right trade-off: builds should be reproducible, not flexible.

## Result

A typical build now runs in 90 seconds. Cold builds (when the dependency layer cache is invalidated) still take about 5 minutes, but those happen maybe once a week.

The compile and test steps are unchanged. We're looking at parallelizing them next.
