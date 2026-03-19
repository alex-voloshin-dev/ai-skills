# Accessibility Audit Checklist (WCAG 2.2 AA)

Comprehensive accessibility checklist for UI/UX design and implementation. Use alongside the `ui-ux-design` skill and UI/UX design guidance. Based on WCAG 2.2 Level AA success criteria.

## Perceivable

### Text Alternatives (1.1)
- [ ] All informational images have descriptive `alt` text
- [ ] Decorative images have empty `alt=""` or are CSS backgrounds
- [ ] Complex images (charts, infographics) have extended descriptions
- [ ] Icons with meaning have accessible labels (aria-label or visually hidden text)
- [ ] Icon-only buttons have accessible names

### Time-Based Media (1.2)
- [ ] Videos have captions (synchronized)
- [ ] Videos have audio descriptions (if visual-only content conveys meaning)
- [ ] Audio content has transcripts
- [ ] Live video has live captions (if applicable)

### Adaptable (1.3)
- [ ] Semantic HTML used throughout: `<header>`, `<nav>`, `<main>`, `<section>`, `<article>`, `<aside>`, `<footer>`
- [ ] Heading hierarchy is logical: H1 → H2 → H3 (no skipping levels)
- [ ] Lists use `<ul>`, `<ol>`, `<dl>` — not styled `<div>`s
- [ ] Tables have `<th>` with `scope`, `<caption>` for data tables
- [ ] Form inputs have associated `<label>` elements
- [ ] Content order in DOM matches visual order
- [ ] Orientation not restricted (works in portrait and landscape)
- [ ] Input purpose identifiable (autocomplete attributes on common fields)

### Distinguishable (1.4)
- [ ] Color is NOT the only means of conveying information (combine with text, icons, patterns)
- [ ] Text color contrast ≥ 4.5:1 against background (normal text)
- [ ] Large text (≥ 18pt or ≥ 14pt bold) contrast ≥ 3:1
- [ ] UI component contrast ≥ 3:1 against adjacent colors (borders, icons, focus indicators)
- [ ] Text resizable to 200% without loss of content or functionality
- [ ] No images of text (except logos)
- [ ] Content reflows at 320px viewport width (no horizontal scrolling)
- [ ] Line height ≥ 1.5× font size for body text
- [ ] Paragraph spacing ≥ 2× font size
- [ ] Content not lost when user overrides spacing (text spacing override test)
- [ ] Hover/focus content dismissible (Escape), hoverable, and persistent

## Operable

### Keyboard Accessible (2.1)
- [ ] All functionality operable via keyboard alone
- [ ] No keyboard traps (Tab moves forward, Shift+Tab moves backward, Escape closes overlays)
- [ ] Keyboard shortcuts do not conflict with browser/OS shortcuts
- [ ] Character key shortcuts can be turned off or remapped (if implemented)

### Enough Time (2.2)
- [ ] Time limits adjustable (extend, turn off) — for session timeouts, auto-advancing content
- [ ] Moving/auto-updating content can be paused, stopped, or hidden
- [ ] No content that flashes more than 3 times per second

### Navigable (2.4)
- [ ] Skip navigation link ("Skip to main content") present and functional
- [ ] Page title (`<title>`) is descriptive and unique per page
- [ ] Focus order is logical and predictable (matches visual layout)
- [ ] Link text is descriptive out of context (not "click here", "read more")
- [ ] Multiple ways to find pages: navigation, search, sitemap
- [ ] Headings and labels are descriptive
- [ ] Focus is visible on all interactive elements (min 2px outline, 3:1 contrast)

### Input Modalities (2.5)
- [ ] Touch targets ≥ 24×24px (WCAG 2.2 AA), recommended ≥ 44×44px
- [ ] Spacing between touch targets prevents accidental activation
- [ ] Functionality available via single pointer (no multi-touch required, unless essential)
- [ ] Drag actions have single-pointer alternative (e.g., up/down buttons for reordering)
- [ ] No motion-activated functions without alternative (e.g., shake-to-undo has a button alternative)

## Understandable

### Readable (3.1)
- [ ] Page language declared: `<html lang="en">`
- [ ] Language changes within content marked: `<span lang="fr">`
- [ ] Reading level appropriate for target audience

### Predictable (3.2)
- [ ] No unexpected context changes on focus (no auto-submit, no auto-navigate)
- [ ] No unexpected context changes on input (unless user is informed beforehand)
- [ ] Navigation is consistent across pages
- [ ] Components with same function have same labels across pages

### Input Assistance (3.3)
- [ ] Input errors identified and described in text (not just color)
- [ ] Labels and instructions provided for all form inputs
- [ ] Error suggestions offered when possible (spell check, format hints)
- [ ] Confirmation step for important actions (financial transactions, data deletion)
- [ ] Redundant entry: previously entered data re-populated (address, payment info)
- [ ] Accessible authentication: no cognitive function test (CAPTCHA has alternative)

## Robust

### Compatible (4.1)
- [ ] HTML validates (no duplicate IDs, proper nesting)
- [ ] Custom components have correct ARIA roles, states, and properties
- [ ] ARIA attribute values are valid
- [ ] Status messages announced to screen readers without focus change (aria-live regions)
- [ ] Dynamic content updates announced appropriately

## Interactive Component Patterns

### Buttons
- [ ] Native `<button>` element (not `<div>` or `<span>` with click handler)
- [ ] Activates on Enter and Space
- [ ] Disabled state uses `disabled` attribute (not just visual styling)
- [ ] Loading state has `aria-busy="true"` and descriptive text

### Links
- [ ] Native `<a href>` element with valid URL
- [ ] Visually distinguishable from surrounding text (not just color — underline or icon)
- [ ] External links indicated (icon + visually hidden "opens in new tab" text)

### Forms
- [ ] Every input has a visible `<label>` (or `aria-label` for icon-only inputs)
- [ ] Required fields indicated with text (not just asterisk or color)
- [ ] Error messages associated with inputs via `aria-describedby`
- [ ] Group related inputs with `<fieldset>` and `<legend>`
- [ ] Autocomplete attributes on relevant fields (name, email, address, phone, credit card)

### Modals / Dialogs
- [ ] Focus trapped inside modal when open
- [ ] Focus moves to modal on open (first focusable element or modal container)
- [ ] Focus returns to trigger element on close
- [ ] Closes on Escape key
- [ ] `role="dialog"` and `aria-modal="true"` present
- [ ] Has `aria-labelledby` pointing to modal title
- [ ] Background content inert (not interactive) when modal is open

### Tabs
- [ ] `role="tablist"`, `role="tab"`, `role="tabpanel"` structure
- [ ] Arrow keys navigate between tabs
- [ ] `aria-selected="true"` on active tab
- [ ] Tab panels associated via `aria-controls` / `aria-labelledby`

### Dropdown / Combobox
- [ ] Activates with Enter/Space (or starts typing for combobox)
- [ ] Arrow keys navigate options
- [ ] Escape closes dropdown
- [ ] Selected option announced by screen reader
- [ ] `aria-expanded` indicates open/close state

### Accordion
- [ ] Trigger is a `<button>` inside a heading element
- [ ] `aria-expanded` indicates open/close state
- [ ] `aria-controls` links trigger to content panel
- [ ] Enter/Space toggles the section

### Toast / Notification
- [ ] Uses `role="status"` or `aria-live="polite"` for informational messages
- [ ] Uses `role="alert"` or `aria-live="assertive"` for urgent messages
- [ ] Dismiss action is keyboard accessible
- [ ] Auto-dismiss allows enough time to read (min 5 seconds, ideally adjustable)

## Testing Tools

| Tool | What It Checks |
|---|---|
| **axe DevTools** | Automated WCAG checks (browser extension) |
| **Lighthouse** | Accessibility score with actionable issues |
| **WAVE** | Visual overlay of accessibility issues |
| **Stark (Figma)** | Contrast checking in design phase |
| **NVDA** (Windows) | Screen reader testing |
| **VoiceOver** (macOS/iOS) | Screen reader testing |
| **JAWS** (Windows) | Screen reader testing (enterprise standard) |
| **Colour Contrast Analyser** | Manual contrast ratio checking |
| **Keyboard-only navigation** | Manual: unplug mouse, Tab through page |

## Quick-Reference Contrast Ratios

| Element | Minimum Ratio (AA) | Enhanced (AAA) |
|---|---|---|
| Normal text (< 18pt) | 4.5:1 | 7:1 |
| Large text (≥ 18pt or ≥ 14pt bold) | 3:1 | 4.5:1 |
| UI components and graphical objects | 3:1 | — |
| Focus indicators | 3:1 | — |
| Placeholder text | 4.5:1 | 7:1 |
