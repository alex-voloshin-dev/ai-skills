---
name: ui-ux-design
description: UI/UX design systems, Figma workflows, accessibility checklists, browser-based visual audit with automated screenshots, component specification patterns, and design-to-code handoff procedures. Use when designing interfaces, creating design systems, auditing accessibility, reviewing existing UI via browser screenshots, specifying components, or preparing design handoff for developers.
disable-model-invocation: true
---

# UI/UX Design

Systematic UI/UX design skill with design system creation guides, Figma workflow patterns, accessibility audit checklists, browser-based visual audit procedures, and design-to-code handoff templates. Produces consistent, accessible, conversion-optimized interfaces.

## When to Use

- Creating or extending a design system (tokens, components, patterns)
- Designing new pages, features, or user flows
- Auditing existing UI for accessibility compliance
- Preparing design specifications for developer handoff
- Setting up Figma project structure and workflows
- Reviewing existing UI via automated browser screenshots and heuristic analysis
- Reviewing UI components against heuristics and platform guidelines

## When NOT to Use

- Writing page content or copy (use `content-creation` skill)
- Implementing frontend code (use `Agent(frontend-engineer)` role)
- Conducting SEO audits (use `/seo-review` workflow)
- Writing technical documentation (use `/docs` workflow)

## Design System Creation

### Step 1: Audit Existing UI

Before creating a design system:

1. **Screenshot inventory**: Capture all existing screens and components
2. **Pattern extraction**: Identify recurring colors, typography, spacing, components
3. **Inconsistency map**: Document where the same concept is implemented differently
4. **Priority matrix**: Rank components by frequency of use × inconsistency severity

### Step 2: Define Foundations

Build from the ground up:

| Foundation | What to Define | Token Naming |
|---|---|---|
| **Color** | Brand, semantic, neutral, overlay palettes | `color-{category}-{shade}` |
| **Typography** | Font families, size scale, weights, line heights | `font-{property}-{size}` |
| **Spacing** | Base unit (4px or 8px), scale | `spacing-{size}` |
| **Border radius** | Scale from none to full | `radius-{size}` |
| **Elevation** | Shadow levels | `shadow-{level}` |
| **Motion** | Duration, easing curves | `motion-{property}-{variant}` |
| **Breakpoints** | Viewport thresholds | `breakpoint-{name}` |

### Step 3: Build Components

Follow Atomic Design progression:

1. **Atoms**: Button, Input, Label, Icon, Badge, Avatar, Checkbox, Radio, Toggle
2. **Molecules**: Input Group, Search Bar, Card, Dropdown, Tooltip, Alert, Breadcrumb
3. **Organisms**: Header, Footer, Sidebar, Form, Data Table, Modal, Navigation

For each component, document:
- **Variants**: Primary, secondary, outline, ghost, destructive
- **Sizes**: xs, sm, md, lg, xl
- **States**: Default, hover, focus, active, disabled, loading, error
- **Accessibility**: ARIA role, keyboard behavior, screen reader announcement
- **Responsive**: Behavior at each breakpoint
- **Do / Don't**: Usage examples and anti-patterns

### Step 4: Document and Maintain

- Publish component library with live examples
- Version with semantic versioning
- Changelog for every update
- Deprecation notices with migration guides

See `design-system-checklist.md` for the full creation checklist.

## Figma Workflow

See `figma-workflow.md` for detailed Figma project setup, component organization, Auto Layout patterns, and developer handoff procedures.

### Quick Reference

| Figma Concept | Code Equivalent |
|---|---|
| Auto Layout | Flexbox / CSS Grid |
| Component variants | React props / variant configs |
| Design tokens (Variables) | CSS custom properties |
| Constraints | CSS positioning / responsive rules |
| Component instances | React component usage |

## Accessibility Audit

See `accessibility-checklist.md` for the comprehensive WCAG 2.2 AA audit checklist.

### Quick Audit (5-Minute Check)

1. **Tab through the page** — can you reach and operate every interactive element?
2. **Zoom to 200%** — does content reflow without horizontal scrolling?
3. **Check contrast** — do all text elements meet 4.5:1 (normal) / 3:1 (large)?
4. **Screen reader test** — do headings, landmarks, and alt text make sense?
5. **Keyboard-only** — can you complete the primary task without a mouse?

## Design-to-Code Handoff

See `assets/handoff-template.md` for the full handoff format — includes component inventory, W3C-format design tokens per component, WCAG 2.2 AA accessibility requirements (with the four new SCs: 2.4.11, 2.5.7, 3.3.7, 3.3.8), animation + reduced-motion contract, edge cases (empty/loading/error/overflow/RTL), browser/device support matrix, and engineer gotchas. Worked example: Button/Primary with measured contrast values and ARIA contract.

## Component Specification

See `assets/component-spec-template.md` for a single-component spec template aligned with Atomic Design, Material Design 3, and Apple HIG. Covers anatomy diagram, variants, props API table, composition rules, accessibility spec, states, responsive behavior, do/don't pairs, related components, and Figma/Storybook reference fields. Worked example: `Card` molecule.

## Templates

- `assets/handoff-template.md` — Design-to-Code handoff format.
- `assets/component-spec-template.md` — Component specification format for design systems.

## Integration

- **Follows rules**: `Agent(ui-ux-designer)` (design principles, accessibility, design systems)
- **Activation**: `@ui-ux-design` (knowledge skill loaded by the `ui-ux-designer` agent — not user-invoked)
- **Used by workflows**: `/feature-dev` (UI features), `/develop` (when ui-ux-designer is in the team)
- **Companion resources**: `design-system-checklist.md`, `figma-workflow.md`, `accessibility-checklist.md`, `visual-audit-checklist.md`, `assets/handoff-template.md`, `assets/component-spec-template.md`
