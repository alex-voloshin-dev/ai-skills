# AI Assets Init Output — File Overwrite

## Problem

User had an existing CLAUDE.md file with custom project notes. Init ran and overwrote it without asking.

Old CLAUDE.md contained:
- Project-specific conventions
- Custom agent definitions
- Team preferences documented

New CLAUDE.md from init generic scaffold.

All custom content lost.

## What Went Wrong

No check for existing CLAUDE.md. No `--overwrite` flag required. No backup created.

User ran init, discovered custom file was destroyed during git diff.

## Safety Issue

Critical files silently destroyed without user confirmation.
