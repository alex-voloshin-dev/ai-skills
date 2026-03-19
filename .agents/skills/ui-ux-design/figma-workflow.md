# Figma Workflow Guide

Best practices for Figma project structure, component organization, design token management, and developer handoff. Use alongside the `ui-ux-design` skill and UI/UX design guidance.

## Project Structure

### File Organization

```
[Project Name]/
├── 🎨 Foundations          # Design tokens and primitives
│   ├── Colors
│   ├── Typography
│   ├── Spacing & Grid
│   ├── Icons
│   └── Elevation & Effects
├── 🧩 Components           # Reusable component library
│   ├── Atoms
│   ├── Molecules
│   └── Organisms
├── 📐 Templates            # Page-level layout templates
│   ├── Marketing Pages
│   ├── App Pages
│   └── Error Pages
├── 📱 Screens              # Actual designs per feature/page
│   ├── [Feature Name]
│   │   ├── Desktop
│   │   ├── Tablet
│   │   └── Mobile
│   └── [Feature Name]
├── 🔄 Prototypes           # Interactive prototypes
│   ├── User Flow A
│   └── User Flow B
└── 📝 Documentation        # Design specs and guidelines
    ├── Design Principles
    ├── Accessibility Guide
    └── Handoff Notes
```

### Naming Conventions

| Element | Convention | Example |
|---|---|---|
| Pages | Emoji + Title Case | `🧩 Components` |
| Frames | PascalCase | `HeroSection`, `NavigationBar` |
| Components | PascalCase with slash hierarchy | `Button/Primary/Large` |
| Variants | Property=Value | `Size=Large, State=Hover` |
| Layers | camelCase | `iconLeft`, `labelText`, `containerMain` |
| Styles | Category/Name | `Color/Primary/500`, `Text/Heading/H1` |
| Variables | category/semantic-name | `color/primary`, `spacing/md` |

## Component Architecture

### Component Properties (Variants)

Define components with Figma's native properties:

```
Button Component Properties:
├── Variant: Primary | Secondary | Outline | Ghost | Destructive
├── Size: sm | md | lg
├── State: Default | Hover | Focus | Active | Disabled | Loading
├── Icon Left: [Boolean] → swap instance
├── Icon Right: [Boolean] → swap instance
├── Label: [Text] → "Button"
└── Full Width: [Boolean]
```

### Auto Layout ↔ Flexbox Mapping

| Figma Auto Layout | CSS Flexbox/Grid |
|---|---|
| Horizontal | `flex-direction: row` |
| Vertical | `flex-direction: column` |
| Spacing between items | `gap` |
| Padding | `padding` |
| Fill container | `flex: 1` / `width: 100%` |
| Hug contents | `width: fit-content` |
| Fixed width | `width: Npx` |
| Space between | `justify-content: space-between` |
| Alignment | `align-items` / `justify-content` |
| Wrap | `flex-wrap: wrap` |

### Auto Layout Best Practices

1. **Everything in Auto Layout**: Every frame, section, and component uses Auto Layout. No absolute positioning unless for overlays/decorative elements
2. **Nesting matches DOM**: Auto Layout hierarchy should mirror the HTML structure developers will build
3. **Use fill/hug consistently**: Fill for containers that stretch, hug for content that sizes to its children
4. **Spacing via gap, not margins**: Use Auto Layout spacing (gap) instead of adding spacer frames
5. **Min/max constraints**: Set min-width/max-width to match responsive behavior

## Design Tokens (Figma Variables)

### Token Architecture

```
Primitive Tokens (raw values):
├── color/blue/500: #3B82F6
├── color/gray/100: #F3F4F6
├── spacing/4: 16px
└── font-size/base: 16px

Semantic Tokens (purpose-mapped):
├── color/primary: {color/blue/500}
├── color/bg/surface: {color/gray/100}
├── spacing/component/padding: {spacing/4}
└── font/body: {font-size/base}

Component Tokens (component-specific):
├── button/bg: {color/primary}
├── button/padding-x: {spacing/component/padding}
└── card/bg: {color/bg/surface}
```

### Variable Collections

| Collection | Purpose | Modes |
|---|---|---|
| **Primitives** | Raw color, spacing, type values | — |
| **Theme** | Semantic mapping | Light, Dark |
| **Density** | Spacing scale | Comfortable, Compact |
| **Breakpoints** | Responsive values | Mobile, Tablet, Desktop |

### Syncing Tokens to Code

1. **Figma → JSON**: Export variables using Figma API or plugins (Tokens Studio, Style Dictionary)
2. **JSON → CSS**: Transform tokens to CSS custom properties via Style Dictionary
3. **CSS → Components**: Reference tokens in component styles
4. **Bidirectional sync**: Changes in Figma propagate to code (and vice versa) via CI pipeline

## Prototyping

### Interaction Patterns

| Trigger | Use For |
|---|---|
| On Click | Buttons, links, cards, menu items |
| While Hovering | Tooltips, preview cards, dropdown menus |
| On Drag | Sliders, drag-and-drop, swipe gestures |
| After Delay | Auto-advance carousels, toast dismissal |
| Mouse Enter/Leave | Hover states, cursor changes |
| Key/Gamepad | Keyboard navigation, shortcuts |

### Prototype Best Practices

1. **Realistic data**: Use real content, not "Lorem ipsum". Content length affects layout
2. **Complete flows**: Prototype end-to-end journeys, not isolated screens
3. **Error states**: Include error paths, empty states, loading states in prototypes
4. **Device-accurate**: Set correct device frame and viewport for testing
5. **Smart Animate**: Use for smooth transitions between states (property changes, position, size, opacity)
6. **Overflow scrolling**: Enable on frames that scroll to test real behavior

## Developer Handoff

### Inspection Setup

1. Enable **Dev Mode** in Figma for developer access
2. Mark frames as **Ready for development** when design is approved
3. Add annotations using Figma's built-in annotation tools:
   - Interaction specs (what happens on click, hover, focus)
   - Responsive behavior notes
   - Accessibility requirements (ARIA roles, keyboard behavior)
   - Edge cases and content overflow behavior

### What Developers Need

| Information | Where in Figma |
|---|---|
| Dimensions, spacing | Inspect panel (auto from Auto Layout) |
| Colors | Variables panel → maps to CSS custom properties |
| Typography | Text styles → maps to CSS classes |
| Assets (icons, images) | Export settings on asset layers |
| Component API | Component properties = React props |
| Interactions | Prototype flow + annotation notes |
| Responsive rules | Multiple frames (mobile/tablet/desktop) + notes |
| Accessibility | Annotation layer with ARIA specs |

### Export Settings

| Asset Type | Format | Scale |
|---|---|---|
| Icons | SVG | 1x |
| Illustrations | SVG (if vector), PNG/WebP (if complex) | 1x, 2x |
| Photos | WebP or AVIF | 1x, 2x |
| Logos | SVG | 1x |
| Favicons | PNG | 16, 32, 48, 180, 192, 512 |

## Figma Plugins (Recommended)

| Plugin | Purpose |
|---|---|
| **Tokens Studio** | Design token management and sync |
| **Stark** | Accessibility contrast checker and simulator |
| **Autoflow** | Draw user flow arrows between frames |
| **Content Reel** | Realistic placeholder content (names, photos, text) |
| **Iconify** | Access to 100K+ icons from popular sets |
| **Lorem Ipsum** | Text generation for different lengths |
| **Contrast** | Quick color contrast ratio checker |
| **A11y Annotation Kit** | Accessibility annotation stamps |

## Collaboration

### Design Review Process

1. **Self-review**: Check against `ui-ux-design` skill checklists before sharing
2. **Design critique**: Present to team with context (user problem, constraints, alternatives considered)
3. **Dev feasibility**: Review with developers for implementation complexity
4. **Accessibility review**: Check with `accessibility-checklist.md`
5. **Approval**: Mark as "Ready for development" in Dev Mode

### Version Control

- **Branching**: Use Figma branches for exploratory work. Merge approved changes to main
- **History**: Save named versions at milestones ("v1.0 — Initial design", "v1.1 — After review feedback")
- **Comments**: Use Figma comments for design discussions. Resolve when addressed
- **Change log**: Maintain a change log page in the Figma file for significant updates
