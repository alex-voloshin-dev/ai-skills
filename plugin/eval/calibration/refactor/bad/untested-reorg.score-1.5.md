# Refactor — Reorganized project structure

## Goal
Move code around to make the project cleaner.

## Changes
- Moved `src/models/` to `src/domain/models/`
- Renamed `services` to `handlers`
- Deleted some unused files (thought they were not needed)
- Changed database imports in 15 files to use the new structure

## Tests
- Some tests are failing because they import from the old location
- Updated imports in the tests to match the new structure
- Did not run the full test suite yet

## Issues
- Deleted a file that turned out to be imported from another project (found out after)
- Not sure if all edge cases are covered by the tests
- The refactor might have broken external consumers who depend on the old module structure

## What Was Changed
- 47 files touched
- 200+ lines changed across imports and file moves
- Some production code modified without clear justification

## Risk
High. Don't know if everything works. May have broken public API.
