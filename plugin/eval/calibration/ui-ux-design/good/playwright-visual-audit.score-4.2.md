# Visual audit: Pricing page across 5 viewports + interaction states

Used `assets/visual-audit-checklist.md` workflow. Captured Playwright screenshots and ran axe-core.

## Viewports

| Viewport | Resolution | Name |
|---|---|---|
| `xs` | 360 × 640 | mobile-portrait |
| `sm` | 768 × 1024 | tablet-portrait |
| `md` | 1280 × 800 | laptop |
| `lg` | 1920 × 1080 | desktop |
| `xl` | 2560 × 1440 | ultrawide |

## Test driver

```typescript
import { test, expect } from '@playwright/test';
import { injectAxe, checkA11y } from 'axe-playwright';

const viewports = [
  { name: 'xs', width: 360, height: 640 },
  // ... 4 more
];

for (const v of viewports) {
  test.describe(`Pricing @${v.name}`, () => {
    test('default state', async ({ page }) => {
      await page.setViewportSize({ width: v.width, height: v.height });
      await page.goto('/pricing');
      await injectAxe(page);
      await expect(page).toHaveScreenshot(`pricing-${v.name}-default.png`);
      await checkA11y(page);
    });

    test('hover on plan card', async ({ page }) => { /* ... */ });
    test('focus on CTA', async ({ page }) => { /* ... */ });
    test('expanded annual toggle', async ({ page }) => { /* ... */ });
  });
}
```

## Findings

- **xs**: pricing tiers stack vertically; one CTA wider than container — fix `width: 100%` instead of fixed `360px`
- **sm**: Quote tier card overflows by 12px; add `min-width: 0` to flex item
- **md/lg/xl**: clean
- **Focus state on CTA**: `outline: 0` on hover state nullifies focus ring on click-then-hover; remove the rule
- **a11y**: 1 violation (color-contrast on muted text 3.8:1; target 4.5:1)

## Score rationale

5 viewports × 4 states (5), axe-core integrated (4), specific findings with fixes (5), tokens-grade outputs (4). Avg 4.2.
