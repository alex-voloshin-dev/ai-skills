# RENAME RUNBOOK — `ai-assets` → `ai-skills`

The in-repo rename (v0.4.0) is complete on branch `rename/ai-assets-to-ai-skills`.
These remaining steps are **git/ops actions outside the working tree** — they cannot
be done by an in-repo edit. Run them yourself, in order.

## 1. Review & merge the rename branch

```
git checkout rename/ai-assets-to-ai-skills
git log --oneline -1          # the v0.4.0 BREAKING rename commit
# review the diff, then:
git checkout main && git merge --no-ff rename/ai-assets-to-ai-skills
```

(Or open a PR from the branch and merge there.)

## 2. Rename the GitHub repository

GitHub → repo **Settings** → rename `ai-assets` → `ai-skills`.
GitHub keeps a redirect, but update the remote explicitly:

```
git remote set-url origin git@github-avav25:alex-voloshin-dev/ai-skills.git
git remote -v        # confirm
git push origin main
```

## 3. Rename the local working directory (optional but consistent)

```
cd ..
mv ai-assets ai-skills
cd ai-skills
```

## 4. Re-register the plugin under the new name

The **running** Claude Code plugin is loaded from the cache
(`~/.claude/plugins/cache/ai-assets/...`) and still uses the old name +
the old `.ai-assets-memory` path until you reinstall. Until then, stale
`.ai-assets-memory/` dirs may be recreated by the cached hooks — harmless,
but reinstall to switch fully:

```
/plugin marketplace remove ai-assets
/plugin marketplace add /absolute/path/to/ai-skills
/plugin install ai-skills
/reload-plugins
```

The new cache path `~/.claude/plugins/cache/ai-skills/...` regenerates on install.

## 5. Post-cutover housekeeping

- Skill/agent invocations are now `/ai-skills:*` (the old `/ai-assets:*` no
  longer resolves — hard cut, by design).
- Project memory was migrated to `.ai-skills-memory/` (history preserved).
- Any external bookmarks/CI referencing the old repo URL: update to `ai-skills`.
- After reinstall, delete leftover stray `.ai-assets-memory/` dirs if any remain:
  `find . -type d -name .ai-assets-memory` then remove.

## Rollback

Nothing was pushed or merged by the automation. To abandon the rename:

```
git checkout main
git branch -D rename/ai-assets-to-ai-skills
mv ~/.claude/ai-skills ~/.claude/ai-assets   # only if it was moved (it was not on this host)
mv .ai-skills-memory .ai-assets-memory        # restore memory dir name
```
