# Visual Audit Checklist — Browser Screenshots and Analysis

Automated browser-based visual audit of existing or newly implemented UI. Use alongside `ui-ux-designer` role and `ui-ux-design` skill. Referenced by `ui-ux-design` skill workflow (Step 3a and Step 11).

## Prerequisites

- Dev server running or production URL accessible
- Playwright installed (`npx playwright install chromium`)

## Launch and Capture

### Screenshot Commands

```bash
# Install Playwright if needed
npx playwright install chromium

# Capture screenshots at multiple viewports
npx playwright screenshot --viewport-size=375,812 <URL> mobile.png
npx playwright screenshot --viewport-size=768,1024 <URL> tablet.png
npx playwright screenshot --viewport-size=1440,900 <URL> desktop.png
npx playwright screenshot --viewport-size=1440,900 --full-page <URL> desktop-full.png
```

### Capture Interaction States

For dynamic pages, use a Playwright script to capture states:

```javascript
// capture-states.js
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();
  await page.goto('<URL>');

  // Default state
  await page.screenshot({ path: 'state-default.png', fullPage: true });

  // Hover state on primary CTA
  const cta = page.locator('button:visible').first();
  if (await cta.count()) {
    await cta.hover();
    await page.screenshot({ path: 'state-hover-cta.png' });
  }

  // Focus state (Tab through)
  await page.keyboard.press('Tab');
  await page.screenshot({ path: 'state-focus-first.png' });

  // Modal/dialog (if trigger exists)
  // await page.click('[data-trigger="modal"]');
  // await page.screenshot({ path: 'state-modal-open.png' });

  // Mobile viewport
  await page.setViewportSize({ width: 375, height: 812 });
  await page.screenshot({ path: 'state-mobile.png', fullPage: true });

  // Scroll through page to trigger viewport animations (framer-motion, etc.)
  const height = await page.evaluate(() => document.body.scrollHeight);
  for (let y = 0; y < height; y += 300) {
    await page.evaluate((scrollY) => window.scrollTo(0, scrollY), y);
    await page.waitForTimeout(100);
  }
  await page.waitForTimeout(500);
  await page.screenshot({ path: 'qa/screenshots/state-scrolled-bottom.png', fullPage: true });

  await browser.close();
})();
```

Run with: `node capture-states.js`

### SPA Animation Handling

Pages with framer-motion, GSAP, or intersection-observer-triggered animations render empty sections on `--full-page` capture because off-screen content hasn't animated in yet.

**Required scroll-through before full-page capture**:

```javascript
// scroll-and-capture.js
const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await page.goto('<URL>', { waitUntil: 'networkidle' });

  // Wait for initial animations
  await page.waitForTimeout(2000);

  // Scroll through entire page to trigger viewport animations
  const height = await page.evaluate(() => document.body.scrollHeight);
  for (let y = 0; y < height; y += 300) {
    await page.evaluate((scrollY) => window.scrollTo(0, scrollY), y);
    await page.waitForTimeout(100);
  }

  // Scroll back to top and wait for re-render
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.waitForTimeout(1000);

  // Now capture — all sections have animated in
  await page.screenshot({ path: 'qa/screenshots/full-page.png', fullPage: true });

  await browser.close();
})();
```

**When to use**: Any SPA with viewport-triggered animations (framer-motion `whileInView`, GSAP ScrollTrigger, Intersection Observer). If the basic `--full-page` capture shows blank sections, switch to this script.

### Screenshot Storage

**Store screenshots in `qa/screenshots/`** (not `tmp/`):
- `tmp/` is commonly blocked by `.codeiumignore` / `.gitignore` and may cause tool failures
- Add `qa/screenshots/*.png` to `.gitignore` to avoid committing binary files
- Use consistent naming: `{page}-{viewport}-{state}.png` (e.g., `home-mobile-default.png`)
- Clean up after audit: delete screenshots that are no longer needed

### Viewport Matrix

| Viewport | Size | Represents |
|---|---|---|
| Mobile portrait | 375×812 | iPhone 13/14/15 |
| Mobile landscape | 812×375 | iPhone landscape |
| Tablet portrait | 768×1024 | iPad |
| Tablet landscape | 1024×768 | iPad landscape |
| Desktop | 1440×900 | Standard laptop |
| Wide desktop | 1920×1080 | External monitor |

Capture at minimum: mobile (375×812), tablet (768×1024), desktop (1440×900).

## Analysis Checklist

Read each captured screenshot and evaluate against these criteria:

### Visual Hierarchy and Layout
- [ ] Clear visual hierarchy — most important elements draw attention first
- [ ] Consistent grid alignment — elements snap to grid, no arbitrary positioning
- [ ] Adequate whitespace — content not cramped, sections clearly separated
- [ ] Logical content flow — information in expected order
- [ ] Above-the-fold content includes key message + CTA (desktop and mobile)
- [ ] Visual balance — no heavy/empty sides

### Typography and Readability
- [ ] Type scale consistent — no arbitrary font sizes
- [ ] Line length 45–75 characters for body text
- [ ] Adequate line height (1.4–1.6 for body)
- [ ] Font size ≥ 16px on mobile
- [ ] Heading hierarchy visually clear (H1 > H2 > H3)
- [ ] No orphaned words in headlines (single word on last line)
- [ ] Text is readable against its background

### Color and Contrast
- [ ] Color palette consistent — no off-brand or random colors
- [ ] Sufficient contrast for text and UI elements (4.5:1 normal text, 3:1 large/UI)
- [ ] Color not sole indicator of meaning (combine with icons, text, patterns)
- [ ] Dark/light mode consistent (if applicable)
- [ ] Semantic colors used correctly (red=error, green=success, yellow=warning)

### Responsive Behavior
Compare mobile vs tablet vs desktop screenshots:
- [ ] No horizontal scrolling on any viewport
- [ ] Content reflows properly — no overlapping or clipping
- [ ] Touch targets adequate on mobile (≥ 44×44px)
- [ ] Navigation usable on all viewports (hamburger menu on mobile if needed)
- [ ] Images scale correctly, no distortion or cropping of important content
- [ ] Font sizes readable on all viewports
- [ ] Spacing proportional across viewports

### Component Consistency
- [ ] Buttons follow consistent style (same variant = same appearance)
- [ ] Inputs, selects, textareas have uniform styling
- [ ] Cards follow consistent layout and spacing
- [ ] Spacing between similar elements is uniform
- [ ] Icons from the same set, consistent size and weight
- [ ] Interactive elements look interactive (affordances — hover states, cursors)
- [ ] Disabled states visually distinct

### Content Quality
- [ ] No placeholder text (Lorem ipsum) in production
- [ ] No broken images or missing assets
- [ ] Copy is readable, scannable, benefit-focused
- [ ] CTAs clear and action-oriented
- [ ] Empty states designed (not just blank space)
- [ ] Error states provide helpful messages
- [ ] Loading states visible (skeletons, spinners, progress bars)

### Performance Indicators (visible in screenshots)
- [ ] No layout shift indicators (content jumping, elements repositioning)
- [ ] Images properly sized (not stretched, pixelated, or oversized)
- [ ] No flash of unstyled content visible
- [ ] Fonts rendered correctly (no FOUT/FOIT)
- [ ] Lazy-loaded images have proper placeholder/skeleton

### Accessibility (Visual Check)
- [ ] Focus indicators visible on interactive elements
- [ ] Sufficient color contrast throughout
- [ ] Text not embedded in images (unreadable by screen readers)
- [ ] No content relying solely on color
- [ ] Touch targets large enough on mobile
- [ ] No extremely small text (< 12px anywhere)

## Findings Report Template

```
## Visual Audit Report

### Audit Info
- **URL**: [target URL]
- **Date**: [date]
- **Mode**: [review / post-implementation verification]
- **Viewports tested**: [list]

### Screenshots Captured
- Mobile (375×812): [path]
- Tablet (768×1024): [path]
- Desktop (1440×900): [path]
- Full page: [path]
- Interaction states: [paths]

### Critical Issues (must fix)
- [ ] [issue] — [screenshot reference] — [fix recommendation]

### Warnings (should fix)
- [ ] [issue] — [screenshot reference] — [fix recommendation]

### Opportunities (improvements)
- [ ] [opportunity] — [screenshot reference] — [recommendation]

### Scores
| Category | Rating | Notes |
|---|---|---|
| Visual hierarchy | [strong / adequate / weak] | |
| Responsive | [pass / issues] | |
| Consistency | [consistent / inconsistencies] | |
| Content | [complete / gaps] | |
| Accessibility (visual) | [pass / issues] | |
| Performance (visual) | [pass / issues] | |

### Delegation
| Fix | Delegate To |
|---|---|
| Layout/CSS fixes | `frontend-engineer` role |
| Content/copy changes | `content-designer` role |
| Accessibility fixes | `frontend-engineer` role + `ui-ux-designer` role |
| SEO issues | `seo-engineer` role |
| Design system gaps | `ui-ux-designer` role |
```

## Post-Implementation Comparison

When verifying implementation against design specs (Step 11):

1. **Place screenshots side-by-side** with design mockups
2. **Check pixel-level alignment**: spacing, sizing, positioning
3. **Verify design tokens applied**: colors match, typography matches, spacing matches
4. **Test all states**: hover, focus, active, disabled, loading, error, empty
5. **Check responsive breakpoints**: layout changes match design spec per viewport
6. **Test animations/transitions**: duration, easing, triggers match spec
7. **Flag deviations**: file as implementation fixes for `frontend-engineer` role
