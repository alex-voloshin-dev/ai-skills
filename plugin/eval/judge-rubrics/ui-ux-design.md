# UI/UX Design Rubric

## Overview

Evaluates `/ui-ux-design` — design systems, accessibility audits, component specs, browser-based visual review, and design-to-engineer handoff. Six dimensions × five levels.

## Dimensions

### Dimension 1: WCAG 2.2 AA Compliance
Addressed all relevant WCAG 2.2 success criteria — including the 2.2 additions: 1.4.3 contrast, 2.4.7 focus visible, 2.4.11 focus not obscured (minimum), 2.5.8 target size (minimum), 3.3.7 redundant entry. Not WCAG 2.1.

- **Level 1:** Accessibility ignored
- **Level 2:** WCAG 2.0/2.1 only; 2.2 additions absent
- **Level 3:** WCAG 2.2 referenced; some new SCs missed
- **Level 4:** All relevant 2.2 SCs cited and met; measurements where applicable (contrast ratio, target size px)
- **Level 5:** All of L4 + automated check evidence (axe-core / Lighthouse / pa11y output)

### Dimension 2: Atomic Design Hierarchy
Components correctly classified as atom / molecule / organism / template / page. Composition relationships explicit.

- **Level 1:** No hierarchy; flat list of "components"
- **Level 2:** Hierarchy named but mis-applied (button labelled organism)
- **Level 3:** Mostly correct; one mis-classification
- **Level 4:** Each component classified correctly with composition trace (organism uses molecule X + atom Y)
- **Level 5:** All of L4 + reuse audit (which atoms/molecules already exist in design system)

### Dimension 3: Design Tokens
Used the W3C Design Tokens Community Group format (`$value` / `$type`) or platform-equivalent (Style Dictionary, Tailwind config). No raw hex / px scattered through specs.

- **Level 1:** Hard-coded hex / px throughout; no token reference
- **Level 2:** Tokens named ad-hoc ("brand-blue") without schema
- **Level 3:** Token format used; coverage incomplete (some hex remains)
- **Level 4:** W3C Design Tokens format ($value / $type) or platform-equivalent; full coverage
- **Level 5:** All of L4 + token tier (primitive → semantic → component) declared

### Dimension 4: Material 3 / HIG Awareness
Applied modern design-system principles where the platform demands it: Material 3 for Android / web; Apple HIG for iOS / macOS; Fluent for Windows. Not blindly mixed.

- **Level 1:** No platform awareness
- **Level 2:** Platform named; principles not applied
- **Level 3:** Some principles applied; conflicts with platform conventions
- **Level 4:** Material 3 or HIG (or platform-correct equivalent) applied throughout
- **Level 5:** All of L4 + cited specific patterns (Material 3 elevation tokens, HIG dynamic type)

### Dimension 5: Visual Audit
For browser-based work, used Playwright (or equivalent) to capture screenshots across viewports + interaction states. Not "looks fine on my screen".

- **Level 1:** No visual evidence
- **Level 2:** One screenshot, one viewport
- **Level 3:** Screenshots across viewports; interaction states absent
- **Level 4:** Screenshots across viewports (mobile / tablet / desktop) + states (default / hover / focus / disabled)
- **Level 5:** All of L4 + automated regression baseline + diff threshold

### Dimension 6: Handoff Template
Used `assets/handoff-template.md` (or skill-shipped equivalent) so engineers can implement without follow-up.

- **Level 1:** No handoff doc; just a Figma link
- **Level 2:** Free-form handoff; missing token references
- **Level 3:** Template used; some sections empty
- **Level 4:** Template fully filled (specs / tokens / states / a11y notes / implementation hints)
- **Level 5:** All of L4 + open questions section + dev-eng owner assignment + sign-off line

## Scoring Logic

- **Aggregate:** average of D1–D6
- **Pass threshold:** 4.0
- **Judge model:** Haiku for routine component specs; Sonnet for accessibility audits or novel layouts

## Anti-Patterns (Auto-Fail)

- WCAG 2.1 cited as the standard (must be 2.2 since Oct 2023)
- Hard-coded hex / px values with no token reference
- Hand-off provided as Figma link only with no document
- "Looks good" visual sign-off without screenshots
- Atomic design hierarchy absent in a multi-component spec

## Calibration Reference

- **Known-good:** `plugin/eval/calibration/ui-ux-design/good/*`
- **Known-bad:** `plugin/eval/calibration/ui-ux-design/bad/*`
