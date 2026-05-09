# Component spec: Alert (molecule)

## Visual

Alerts use these colours per type:

| Type | Background | Text | Border |
|---|---|---|---|
| Info | `#E0F2FE` | `#0C4A6E` | `#BAE6FD` |
| Success | `#DCFCE7` | `#14532D` | `#BBF7D0` |
| Warning | `#FEF3C7` | `#78350F` | `#FDE68A` |
| Error | `#FEE2E2` | `#7F1D1D` | `#FECACA` |

Spacing: 16px padding, 12px between icon and text. Border-radius 8px. Max-width 480px. Margin-bottom 16px.

Font: 14px / 1.5 line-height.

---

**What's wrong with this output**:

1. **Hard-coded hex values everywhere**. The design system has tokens (e.g., `color-feedback-info-bg`, `color-feedback-success-fg`) and this spec ignored them. Now any token rename breaks the spec; any theme variant (dark mode, density) requires re-specifying every value.
2. **No reference to W3C Design Tokens format** ($value/$type) which is the 2024+ interop standard.
3. **Magic numbers without semantic names**. "16px padding" should be `space-alert-padding-y` (or equivalent token); "8px radius" should be `radius-control-md`. Same for the font-size; the spec should cite `font-body-md` not `14px / 1.5`.
4. **Result**: alert component becomes a one-off; cannot be themed; every token rename breaks it; no consistency with other components (Card, Button, Badge already use tokens).
5. **No light/dark/high-contrast variants**. With hard-coded hex, dark mode requires duplicating the entire spec. Tokens with mode-aware values would handle this in one definition.
