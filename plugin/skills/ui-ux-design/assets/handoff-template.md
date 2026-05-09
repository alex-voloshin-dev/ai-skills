# Design-to-Code Handoff Template

Use this template when handing off a screen, flow, or component set from design to engineering. Fill in every section that applies — empty sections are removed, not left as `TBD`. Aligns with Material Design 3 (`m3.material.io`) and Apple Human Interface Guidelines structure for component descriptions, and uses the W3C Design Tokens Community Group format (`{$value, $type}`) for portability.

## 1. Component Inventory

For each component included in the handoff, fill out one row.

| Component | Design source (Figma node URL) | Breakpoints handled | States covered |
|---|---|---|---|
| `Button/Primary` | `figma.com/file/<id>?node-id=42:108` | xs (320), sm (640), md (768), lg (1024), xl (1440) | default, hover, focus-visible, active, disabled, loading |
| `Card/Article` | `figma.com/file/<id>?node-id=42:212` | sm, md, lg | default, hover, focus-within, error |

## 2. Design Tokens Per Component

Use W3C Design Tokens format. One block per component.

```json
{
  "Button/Primary": {
    "color": {
      "background-default":  { "$value": "#0B5CD7", "$type": "color" },
      "background-hover":    { "$value": "#0A52BD", "$type": "color" },
      "background-active":   { "$value": "#08438C", "$type": "color" },
      "background-disabled": { "$value": "#0B5CD740", "$type": "color" },
      "label":               { "$value": "#FFFFFF", "$type": "color" }
    },
    "typography": {
      "label": {
        "$value": { "fontFamily": "Inter", "fontWeight": 600, "fontSize": "14px", "lineHeight": "20px", "letterSpacing": "0.01em" },
        "$type": "typography"
      }
    },
    "spacing": {
      "padding-y": { "$value": "10px", "$type": "dimension" },
      "padding-x": { "$value": "16px", "$type": "dimension" },
      "gap-icon-label": { "$value": "8px", "$type": "dimension" }
    },
    "radius": { "corner": { "$value": "8px", "$type": "dimension" } }
  }
}
```

## 3. Accessibility Requirements Per Component

For each component, declare WCAG 2.2 AA criteria the implementation must satisfy. Cite SCs by number — including the four new in WCAG 2.2: 2.4.11 Focus Not Obscured (Minimum), 2.5.7 Dragging Movements, 3.3.7 Redundant Entry, 3.3.8 Accessible Authentication (Minimum).

**Button/Primary**:
- ARIA role: implicit (`<button>` element). For icon-only variant, add `aria-label`.
- Keyboard: `Enter` and `Space` activate. `Tab` enters / leaves. No custom shortcuts.
- Focus management: visible focus ring, never `outline: none` without replacement (WCAG 2.4.7 Focus Visible).
- Focus indicator must NOT be hidden by sticky headers, toasts, or modals (WCAG 2.4.11 Focus Not Obscured (Minimum), AA).
- Screen reader: announces label text + state (`disabled`, `pressed` if toggle).
- Color contrast measured with Figma "Contrast" plugin or `WebAIM Contrast Checker`:
  - Label on default background: `#FFFFFF` on `#0B5CD7` = 5.86:1 (passes 4.5:1 normal text).
  - Disabled state: `#FFFFFF` on `#0B5CD740` over `#FFFFFF` page = 1.41:1 — disabled text is exempt from 1.4.3 but informative pattern still required (recommend non-color affordance: cursor `not-allowed`, `aria-disabled="true"`).
- Hit target: 44x44 CSS px minimum (WCAG 2.5.8 Target Size (Minimum), AA in 2.2). Visually 36px tall — pad the hit area transparently or bump height.

## 4. Animations & Transitions

| Trigger | Property | Duration | Easing | Reduced-motion fallback |
|---|---|---|---|---|
| hover enter | `background-color` | 120ms | `cubic-bezier(0.4, 0, 0.2, 1)` (M3 standard easing) | instant swap |
| focus-visible | `box-shadow` (focus ring) | 80ms | `linear` | instant swap |
| loading state | spinner rotate | 800ms loop | `linear` | replace with static "Loading…" text |

Always wrap motion in `@media (prefers-reduced-motion: reduce)` and either remove the transition or shorten to `<= 50ms`. Never autoplay loops > 5s (WCAG 2.2.2).

## 5. Edge Cases

For every component:
- **Empty state**: what renders when there is no data (illustration, copy, primary action).
- **Loading state**: skeleton vs. spinner vs. progress bar; aria-live region announcement.
- **Error state**: visual treatment, recovery action, focus moves to the error message (WCAG 3.3.1 Error Identification).
- **Long-content overflow**: truncation strategy (`text-overflow: ellipsis`, line-clamp, expand-on-hover, full-text on focus).
- **RTL support**: mirror the layout (paddings flip, icons swap chevron direction, do NOT mirror logos or numerals).

Concrete example — Button/Primary:
- Empty state: N/A (button is always rendered with a label).
- Loading: spinner replaces icon, label becomes "Loading…", `aria-busy="true"`, button is `aria-disabled="true"` but stays focusable so screen readers can read state changes.
- Error: button shakes (8px horizontal, 200ms, 2 cycles) — disabled under `prefers-reduced-motion`. Error message rendered in adjacent `role="alert"` region.
- Long label: `max-width: 320px`, single line with ellipsis. Full text on `title` attribute and visible tooltip on hover/focus.
- RTL: leading icon swaps to trailing position; `padding-inline-start` / `padding-inline-end` (logical properties) instead of `padding-left/right`.

## 6. Browser & Device Support Matrix

| Tier | Browsers | Screen sizes | Pointer types |
|---|---|---|---|
| Tier 1 (full QA) | Chrome 120+, Safari 17+, Firefox 120+, Edge 120+ | 360–1920px | mouse, touch, stylus |
| Tier 2 (smoke) | Chrome 110–119, Safari 16, Samsung Internet 23+ | 320–2560px | mouse, touch |
| Tier 3 (graceful degrade) | iOS Safari 15, older Chromium-based | 280–360px | touch only |

Notes: respect `@media (pointer: coarse)` for touch-tier hit targets; verify on a real iOS device for `100vh` quirks.

## 7. Implementation Notes for Engineer (gotchas)

- Use `:focus-visible`, not `:focus`, so keyboard users see the ring without mouse-click flash.
- Use logical CSS properties (`padding-inline-*`, `margin-block-*`) so RTL works without overrides.
- For the loading spinner, use an SVG with `<animateTransform>` or CSS keyframes — never an animated GIF (cannot pause for reduced-motion).
- Don't lock the button width on label change — use `min-width` instead so "Loading…" doesn't reflow neighbors.
- Test with browser zoom at 200% and 400%; content must reflow without horizontal scroll (WCAG 1.4.10 Reflow).
- If this button submits a form, verify autofill values are not silently cleared on submit (WCAG 3.3.7 Redundant Entry).
