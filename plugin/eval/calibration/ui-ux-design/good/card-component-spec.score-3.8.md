# Component spec: Card (molecule)

Used `assets/component-spec-template.md`. Concrete worked example — Card molecule for the project's design system.

## Anatomy

```
┌──────────────────────────────────┐
│ [Optional image area, 16:9]      │
├──────────────────────────────────┤
│ Heading                          │
│ Supporting text                  │
│                                  │
│ [Action / Action-secondary]      │
└──────────────────────────────────┘
```

## Variants (Material 3)

- `elevated`: shadow-1; surface tint
- `filled`: secondary container colour; no elevation
- `outlined`: 1px outline; transparent surface

## Props API

| Prop | Type | Default | Description | Required |
|---|---|---|---|---|
| `variant` | "elevated" \| "filled" \| "outlined" | "elevated" | Visual variant | no |
| `interactive` | boolean | false | If true, whole card is a link/button target with focus ring | no |
| `image` | ReactNode | — | Optional 16:9 image area | no |
| `heading` | string | — | Card title | yes |
| `supportingText` | ReactNode | — | Body content | no |
| `actions` | ReactNode | — | Slot for action area | no |

## Composition

- Atoms allowed inside: Image, Heading, Text, Button, Badge, Icon
- Molecules forbidden: Card (no nesting Cards)
- Organisms forbidden inside

## A11y (WCAG 2.2 AA)

- 1.3.1 Info & Relationships — semantic structure (`<article>` for the card, `<h3>` for heading, `<p>` for body)
- 1.4.3 Contrast — text on each variant's surface ≥ 4.5:1
- 2.4.7 Focus Visible — when `interactive`, focus ring on the wrapper
- 4.1.2 Name, Role, Value — when `interactive`, wrapper is `<a>` or `<button>`

## Tokens

`color-surface-card-elevated`, `color-surface-card-filled`, `color-outline-card`, `space-card-padding`, `radius-card`, `shadow-card-1`, `font-card-heading`, `font-card-body`.

## Score rationale

Atomic-design role explicit (4), Material 3 variants applied (4), props table complete (4), WCAG SCs by number (4), tokens cited (3.5). Avg 3.8.
