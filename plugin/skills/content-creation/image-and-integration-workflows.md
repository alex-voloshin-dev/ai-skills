# Image Generation, Integration, and Measurement Workflows

Companion to `@content-tools`. Covers AI image generation workflows, external service integration, MCP integration points, content brief templates, and content performance measurement.

## AI Image Generation Workflows

### Hero Image Generation

**Prompt structure** (works for Midjourney v7, GPT-Image-1, Flux 1.1 Pro, Ideogram, Stable Diffusion):
```
[Subject description], [style], [mood/atmosphere], [color palette], [composition], [technical specs]
```

For Sora 2 / Runway / Kling video prompts, append: `[motion / camera direction], [duration], [framing]`.

**Examples by page type**:

| Page Type | Prompt Pattern |
|---|---|
| **SaaS landing** | `Clean minimal dashboard interface showing [feature], soft gradient background in [brand colors], isometric perspective, professional, modern --ar 16:9` |
| **Product page** | `Product screenshot mockup on [device] with [context elements], studio lighting, [brand color] accents, photorealistic --ar 3:2` |
| **About page** | `[Scene showing team/culture], candid style, warm natural lighting, shallow depth of field, authentic not staged --ar 16:9` |
| **Blog header** | `Abstract illustration representing [topic concept], [brand style] aesthetic, [2-3 colors], editorial illustration style --ar 2:1` |

### Illustration Style Consistency

To maintain visual consistency across AI-generated illustrations:

1. **Create a style reference**: Generate one illustration you love, save as reference
2. **Build a prompt template**: Lock the style portion, vary only the subject
3. **Consistent parameters**: Same aspect ratio, same style keywords, same negative prompts
4. **Color palette lock**: Always include your brand colors in the prompt
5. **Batch generation**: Generate all illustrations for a page/section in one session

**Template**:
```
[Subject for this specific illustration], in the style of [reference description], 
flat vector illustration, [brand color 1] and [brand color 2] color scheme, 
clean lines, minimal detail, white background, modern tech aesthetic --ar 4:3
```

### Image Quality Checklist

Before using any AI-generated image:

- [ ] No visual artifacts (extra fingers, distorted text, weird shadows)
- [ ] No recognizable faces of real people (legal risk)
- [ ] No copyrighted logos or brand elements
- [ ] Matches brand color palette
- [ ] Appropriate resolution for intended use (min 2x for retina)
- [ ] Represents diversity inclusively and naturally
- [ ] No stereotypical or biased representations
- [ ] Commercial license confirmed per tool's ToS

## External Service Integration

### Content Management Workflow

```
1. BRIEF → Create content brief (audience, goal, tone, keywords)
     ↓
2. DRAFT → Generate first draft with AI (text + image concepts)
     ↓
3. EDIT → Human review: brand voice, accuracy, legal, accessibility
     ↓
4. DESIGN → Place content in design (Figma) with visuals
     ↓
5. REVIEW → Design + content review together (not separate)
     ↓
6. OPTIMIZE → A/B test variants, measure, iterate
     ↓
7. PUBLISH → Deploy with proper meta tags, structured data, analytics
```

### MCP Integration Points

When using MCP servers for content workflows:

| MCP Server | Use Case |
|---|---|
| **Figma MCP** | Read design specs, extract text content, sync design tokens |
| **GitHub MCP** | Commit content changes, create PRs for content updates |
| **CMS MCP** (if available) | Push content directly to CMS, manage content versions |
| **Analytics MCP** (if available) | Pull performance data for content optimization |

### Content Brief Template

```markdown
# Content Brief: [Page/Section Name]

## Audience
- **Who**: [target persona]
- **Journey stage**: [awareness / consideration / decision]
- **What they know**: [existing knowledge level]
- **What they feel**: [current emotional state — frustrated, curious, skeptical]

## Objective
- **Primary goal**: [what user should do — sign up, buy, learn]
- **Secondary goal**: [what else — share, explore, bookmark]
- **Success metric**: [conversion rate, time on page, scroll depth]

## Message
- **Key message**: [one sentence — the takeaway]
- **Supporting points**: [3-4 proof points]
- **Objections to address**: [what might stop them]
- **Tone**: [specific tone for this piece]

## SEO
- **Primary keyword**: [target keyword]
- **Secondary keywords**: [2-3 related terms]
- **Search intent**: [informational / commercial / transactional]

## Visual Direction
- **Hero image**: [description of ideal visual]
- **Supporting visuals**: [screenshots, illustrations, icons needed]
- **Style reference**: [links to inspirational examples]

## Constraints
- **Word count**: [target length]
- **Deadline**: [date]
- **Approvals needed**: [who must review]
```

## Measurement and Optimization

### Content Performance Metrics

| Metric | Tool | Target |
|---|---|---|
| **Conversion rate** | Google Analytics, Mixpanel | Varies by page type |
| **Bounce rate** | Google Analytics | < 40% for landing pages |
| **Time on page** | Google Analytics | > 2 min for content pages |
| **Scroll depth** | Hotjar, GA4 | > 75% reach CTA |
| **Click-through rate** | GA4, heatmaps | > 3% for primary CTA |
| **Readability score** | Hemingway Editor | Grade 7-9 |

### A/B Testing Priorities

Test in this order (highest impact first):

1. **Headlines** — biggest impact on engagement and bounce rate
2. **CTAs** — text, color, size, placement
3. **Hero image** — product screenshot vs illustration vs lifestyle photo
4. **Social proof** — placement, format, content
5. **Page length** — short vs long-form
6. **Form fields** — number, order, labels
