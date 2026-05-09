# Component Specification Template

Use this template to specify a single component for a design system. Aligned with Atomic Design (Frost), Material Design 3 component-level documentation, and Apple Human Interface Guidelines structure. The example below specifies a `Card` component end-to-end so each section is concrete.

## 1. Name & Atomic Role

- **Component name**: `Card`
- **Atomic level**: molecule (composes Heading atom + Body Text atom + Image atom + optional Button atom).
- **Role in product**: surface that groups related content and a primary action. Used in lists, grids, and dashboards.

## 2. Visual Anatomy

```
+------------------------------------------+
|  [ media ]                               |  <- optional: image, video poster, icon
|------------------------------------------|
|  Eyebrow label (optional)                |  <- category, timestamp
|  Title (h3)                              |  <- 1–2 lines, ellipsis after
|  Body copy (2–4 lines)                   |  <- summary; line-clamp at lg
|                                          |
|  [ Action button ] [ Secondary link ]    |  <- 0–2 actions
+------------------------------------------+
```

Slots: `media`, `eyebrow`, `title` (required), `body`, `actions`.

## 3. Variants

Following Material Design 3 card taxonomy adapted for the system:

| Axis | Values |
|---|---|
| **Type** | `elevated`, `filled`, `outlined` |
| **Size** | `sm` (240px), `md` (320px), `lg` (480px) |
| **Density** | `comfortable` (default), `compact` (-25% vertical padding) |
| **Color theme** | inherits from parent (`light`, `dark`, `high-contrast`) |

Combinatorial constraint: `compact` density disables `media` slot for `sm` size (insufficient height).

## 4. Properties / Props API

| Prop | Type | Default | Required | Description |
|---|---|---|---|---|
| `type` | `'elevated' \| 'filled' \| 'outlined'` | `'elevated'` | no | Visual treatment. |
| `size` | `'sm' \| 'md' \| 'lg'` | `'md'` | no | Width preset. |
| `density` | `'comfortable' \| 'compact'` | `'comfortable'` | no | Vertical padding scale. |
| `title` | `string` | — | yes | Card heading text; renders as `h3` by default. |
| `headingLevel` | `2 \| 3 \| 4 \| 5 \| 6` | `3` | no | Allows correct outline nesting (WCAG 1.3.1, 2.4.6). |
| `media` | `ReactNode` | — | no | Image / video / icon slot. |
| `actions` | `ReactNode` | — | no | Up to 2 action elements; more triggers a dev warning. |
| `interactive` | `boolean` | `false` | no | Whole card becomes one focusable target with `role="link"` or `role="button"`. |
| `href` | `string` | — | no | Required when `interactive` and behavior is navigation. |
| `onClick` | `(e) => void` | — | no | Required when `interactive` and behavior is action. |
| `aria-label` | `string` | — | conditional | Required when `interactive` and the visible title is not a sufficient accessible name. |

## 5. Composition Rules

**Can nest inside Card**: text atoms, Image, Badge, Tag, Button (max 2), inline links, Avatar.

**Cannot nest inside Card**: another Card, Modal, full-page layout components (Header, Footer), Form (use a dedicated Form component).

**Card cannot be nested inside**: Button, Link, another interactive Card (no nested interactive elements per WCAG 4.1.2 + ARIA APG button pattern).

## 6. Accessibility Specification

WCAG 2.2 AA criteria addressed:

- **1.3.1 Info and Relationships** — heading rendered as the configured `headingLevel`; eyebrow uses `<p>` not a heading.
- **1.4.3 Contrast (Minimum)** — title vs surface ≥ 4.5:1; body vs surface ≥ 4.5:1; outlined border vs surface ≥ 3:1.
- **1.4.11 Non-text Contrast** — interactive card focus ring ≥ 3:1 vs adjacent colors.
- **2.1.1 Keyboard** — when `interactive`, the whole card is one Tab stop; `Enter` activates (and `Space` if `role="button"`).
- **2.4.7 Focus Visible** — 2px outline offset 2px, system-token `focus-ring` color.
- **2.4.11 Focus Not Obscured (Minimum)** — sticky headers / sheets must not cover the card's focus ring; document scroll-margin: 80px.
- **2.5.8 Target Size (Minimum)** — when `interactive`, hit area ≥ 24x24 CSS px (AA); inner action buttons ≥ 44x44.
- **3.3.7 Redundant Entry** — N/A unless card contains a form.
- **4.1.2 Name, Role, Value** — interactive card exposes accessible name = title; role = `link` or `button` per behavior.

**Focus order**: media (if it is a link of its own — usually not) → title link / card itself → actions left-to-right.
**Keyboard shortcuts**: none specific to Card; respects parent list's roving tabindex if used in a grid.

## 7. States

| State | Visual change | Behavior change |
|---|---|---|
| default | base styles | — |
| hover (interactive only) | elevation +1, cursor `pointer` | — |
| focus-visible | 2px focus ring, offset 2px | — |
| active | elevation -1 (pressed feel) | — |
| selected | accent border 2px + check icon top-right | `aria-pressed="true"` or `aria-current` |
| disabled | 38% opacity, cursor `not-allowed` | `aria-disabled="true"`, not focusable |
| loading | skeleton in title/body slots, shimmer animation | `aria-busy="true"` |
| error | error border + inline message slot | `role="alert"` on message |

## 8. Responsive Behavior

| Breakpoint | Behavior |
|---|---|
| xs (< 640) | size auto-clamps to `sm`; media stacks above content (always); actions wrap to new row. |
| sm (640–767) | size respects prop; media still stacks. |
| md (768–1023) | media may sit beside content if `mediaPosition="start"`. |
| lg (1024–1439) | full prop-driven layout. |
| xl (≥ 1440) | same as lg; max-width clamp at `lg` size. |

Reflow at 320px viewport (WCAG 1.4.10). Logical properties for RTL.

## 9. Usage Examples

**Do**:
- Use Card to group a single concept (one article, one product, one user). One title per card.
- Make the entire card interactive when the primary action is "open detail" — fewer click targets for users with motor impairments.
- Pair `headingLevel` with surrounding outline so screen reader users can navigate by heading.

**Don't**:
- Don't nest more than 2 actions; more = use a Menu in an overflow button.
- Don't put a form inside a Card whose body is also clickable — nested interactive areas confuse keyboard and AT users.
- Don't rely on color alone to indicate `selected` state — the check icon is mandatory (WCAG 1.4.1).
- Don't disable Card focus ring for "design polish" — see Apple HIG: focus indicators are part of the system contract.

## 10. Related Components

- **Composed of**: `Heading`, `Text`, `Image`, `Button`, `Badge`.
- **Composes with**: `Grid`, `List`, `Tabs` (as content), `Carousel`.
- **Alternatives**: `ListItem` (for dense rows), `Tile` (for media-first launchers), `Banner` (for full-width promotional surfaces).

## 11. Implementation References

- Figma: `figma.com/file/<file-id>?node-id=<card-component-id>` (canonical source).
- Storybook: `storybook.<product>.com/?path=/docs/molecules-card--docs` (placeholder; populate after first build).
- Engineering RFC: `docs/rfcs/0042-card-component.md`.
- Material 3 reference: `m3.material.io/components/cards/overview` (informative).
- Apple HIG reference: `developer.apple.com/design/human-interface-guidelines/lists-and-tables` (informative).
