# Design System Creation Checklist

Comprehensive checklist for building a design system from scratch or auditing an existing one. Use alongside `@ui-ux-designer` role and `ui-ux-design` skill.

## Phase 1: Audit and Discovery

### Inventory
- [ ] Screenshot all existing screens (desktop + mobile)
- [ ] Catalog all unique components currently in use
- [ ] Document all color values in use (hex, RGB, HSL)
- [ ] Document all font families, sizes, and weights in use
- [ ] Document all spacing values (padding, margin, gap)
- [ ] Document all border-radius values
- [ ] Document all shadow/elevation values
- [ ] Identify icon sets currently in use

### Analysis
- [ ] Map inconsistencies: same component with different implementations
- [ ] Map redundancies: different components serving the same purpose
- [ ] Identify most-used components (priority for standardization)
- [ ] Review current accessibility compliance level
- [ ] Check responsive behavior patterns
- [ ] Document current naming conventions (CSS classes, components)

## Phase 2: Foundations (Design Tokens)

### Color System
- [ ] Define brand colors (primary, secondary) with full shade scales (50–950)
- [ ] Define semantic colors: success, warning, error, info with shade scales
- [ ] Define neutral palette: gray scale for text, backgrounds, borders
- [ ] Define overlay/alpha colors for modals, backdrops
- [ ] Verify all text/background combinations meet WCAG 2.2 AA contrast (4.5:1 normal, 3:1 large)
- [ ] Design for color blindness: test with protanopia, deuteranopia, tritanopia simulators
- [ ] Define dark mode palette (semantic tokens mapping to different primitives)
- [ ] Export as CSS custom properties: `--color-{category}-{shade}`

### Typography
- [ ] Select primary font (body text) — prioritize readability and web performance
- [ ] Select secondary font (headings, display) — if different from primary
- [ ] Define type scale: minimum 6 sizes (xs, sm, base, lg, xl, 2xl, 3xl, 4xl)
- [ ] Define font weights: regular (400), medium (500), semibold (600), bold (700)
- [ ] Define line heights: tight (1.25), normal (1.5), relaxed (1.75)
- [ ] Define letter spacing for headings (slight negative) and body (normal)
- [ ] Verify minimum 16px body text on mobile
- [ ] Test text at 200% zoom — no overflow, no truncation
- [ ] Export as tokens: `--font-size-{name}`, `--font-weight-{name}`, `--line-height-{name}`

### Spacing
- [ ] Define base unit: 4px (compact) or 8px (spacious)
- [ ] Define spacing scale: 0, 0.5, 1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24
- [ ] Apply consistently: component padding, element gaps, section margins
- [ ] Document spacing guidelines: when to use which values
- [ ] Export as tokens: `--spacing-{value}`

### Border Radius
- [ ] Define radius scale: none (0), sm (2px), md (4px), lg (8px), xl (12px), 2xl (16px), full (9999px)
- [ ] Assign defaults: buttons (md), cards (lg), inputs (md), avatars (full), modals (xl)
- [ ] Export as tokens: `--radius-{name}`

### Elevation (Shadows)
- [ ] Define shadow levels: sm, md, lg, xl (1–4 levels minimum)
- [ ] Shadows indicate interactivity level: higher elevation = more interactive / closer to user
- [ ] Verify shadows visible in both light and dark modes
- [ ] Export as tokens: `--shadow-{level}`

### Motion
- [ ] Define duration scale: fast (150ms), normal (250ms), slow (350ms)
- [ ] Define easing curves: ease-out (entering), ease-in (exiting), ease-in-out (state change)
- [ ] Respect `prefers-reduced-motion`: disable animations when user requests
- [ ] Document which transitions apply to which interactions
- [ ] Export as tokens: `--motion-duration-{name}`, `--motion-easing-{name}`

### Breakpoints
- [ ] Define breakpoints: sm (640px), md (768px), lg (1024px), xl (1280px), 2xl (1536px)
- [ ] Document layout behavior at each breakpoint
- [ ] Define container max-widths per breakpoint
- [ ] Export as tokens: `--breakpoint-{name}`

## Phase 3: Components

### Component Specification Template

For each component, verify:

- [ ] **Variants defined**: primary, secondary, outline, ghost, destructive (as applicable)
- [ ] **Sizes defined**: sm, md, lg (as applicable)
- [ ] **All states designed**: default, hover, focus, active, disabled, loading, error, selected
- [ ] **Responsive behavior documented**: how it adapts at each breakpoint
- [ ] **Accessibility specified**: ARIA role, keyboard interactions, screen reader behavior
- [ ] **Spacing uses tokens only**: no magic numbers
- [ ] **Colors use semantic tokens**: not primitive color values
- [ ] **Typography uses scale**: not arbitrary font sizes
- [ ] **Do/Don't examples**: at least 2 of each

### Core Components Checklist

#### Atoms
- [ ] Button (primary, secondary, outline, ghost, destructive, icon-only)
- [ ] Input (text, number, email, password, search, textarea)
- [ ] Label
- [ ] Checkbox
- [ ] Radio
- [ ] Toggle / Switch
- [ ] Select / Dropdown trigger
- [ ] Badge / Tag
- [ ] Avatar
- [ ] Icon (consistent set: Lucide, Phosphor, or custom)
- [ ] Divider / Separator
- [ ] Skeleton / Placeholder
- [ ] Spinner / Loading indicator

#### Icon Set Management

When using an icon library (Solar, Lucide, Phosphor, Heroicons, etc.):

- [ ] **Single icon set chosen** — do not mix icon libraries within one project
- [ ] **Variant convention established** — pick one variant (e.g., `bold-duotone`, `outline`, `solid`) as default; document when to use alternatives
- [ ] **Icon registry exists** — a central file or config that maps icon names to components/imports
- [ ] **Registration check before use** — every icon referenced in UI code must exist in the registry; unregistered icons cause runtime errors or missing visuals
- [ ] **Validation command documented** — e.g., `grep -roh "icon-prefix:[a-z-]*" src/ | sort -u` cross-checked against registry file
- [ ] **Pre-commit hook or CI check** — automate icon registration validation to catch missing icons before deploy
- [ ] **Naming convention** — consistent kebab-case naming matching the icon library's convention
- [ ] **Icon sizing** — uses design tokens (`--icon-size-sm`, `--icon-size-md`, `--icon-size-lg`), not arbitrary pixel values

#### Molecules
- [ ] Input Group (label + input + helper text + error message)
- [ ] Search Bar
- [ ] Card (media, content, actions)
- [ ] Dropdown Menu
- [ ] Tooltip
- [ ] Popover
- [ ] Alert / Banner
- [ ] Breadcrumb
- [ ] Pagination
- [ ] Tabs
- [ ] Accordion
- [ ] Progress Bar
- [ ] Toast / Notification

#### Organisms
- [ ] Header / Navigation Bar
- [ ] Footer
- [ ] Sidebar / Drawer
- [ ] Form (with validation patterns)
- [ ] Data Table (sortable, filterable, paginated)
- [ ] Modal / Dialog
- [ ] Command Palette
- [ ] Empty State
- [ ] Error Page (404, 500, generic)

## Phase 4: Documentation

- [ ] Design principles documented (3–5 core principles)
- [ ] Getting started guide for designers
- [ ] Getting started guide for developers
- [ ] Token reference with all values
- [ ] Component catalog with live examples
- [ ] Pattern library (common layouts, page templates)
- [ ] Accessibility guidelines
- [ ] Contribution guide (how to propose new components)
- [ ] Changelog format established
- [ ] Version numbering (semantic versioning)

## Phase 5: Governance

- [ ] Component ownership defined (who maintains what)
- [ ] Review process for new components
- [ ] Deprecation policy documented
- [ ] Update cadence established (monthly reviews)
- [ ] Design-dev sync process (how token changes propagate)
- [ ] Quality gates: new components must pass accessibility audit before inclusion
