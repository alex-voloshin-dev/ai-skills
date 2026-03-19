# Content Tools Guide

Detailed workflows for AI content generation tools, prompting techniques, and integration with external services. Use alongside `Agent(content-designer)` role and `content-creation` skill.

## Content Research Workflows

Systematic research phase before content creation. Applies to blog posts, articles, and public-facing content.

### Topic Research

**Goal**: Understand the topic landscape before writing.

**Steps**:

1. **Web search** — find 3-5 top-ranking articles for the target keyword. For each, note:
   - Angle and depth (surface-level vs deep-dive)
   - Content gaps (what they miss, what they get wrong)
   - Word count and structure
   - Publication date (freshness)
2. **Competitive content audit** — search competitor blogs for the same topic. Identify:
   - What angle competitors take
   - What unique data or perspective you can add
   - Content format differences (listicle vs guide vs case study)
3. **Keyword research** — identify search intent and related terms:
   - Primary keyword (main topic)
   - Secondary keywords (2-3 related terms for H2 headings)
   - Search intent: informational ("how to"), commercial ("best tools for"), transactional ("buy/sign up")
   - Long-tail variations for FAQ or subsections

### Data and Fact Gathering

**Goal**: Collect citable data points to strengthen the content.

**Steps**:

1. **Find statistics** — search for recent studies, surveys, benchmarks:
   - Prefer primary sources (original study) over secondary (blog citing a study)
   - Note publication date — discard data older than 2-3 years unless it's a foundational study
   - Save exact citation: author, organization, year, URL
2. **Fact-check** — verify every claim before including it:
   - Cross-reference with at least 2 independent sources
   - Check if the stat is used in correct context (not cherry-picked)
   - If a stat seems too good to be true — verify the methodology
3. **Expert quotes** — find relevant quotes from industry experts:
   - Conference talks, podcasts, published interviews
   - Always attribute with name, title, context

### Existing Content Audit

**Goal**: Identify cross-linking opportunities within the project's blog.

**Steps**:

1. **Scan blog directory** — list all existing posts with titles and topics
2. **Map relevance** — for each existing post, rate cross-link potential (high / medium / none)
3. **Plan bidirectional links**:
   - From new post → existing posts (minimum 3 internal links)
   - From existing posts → new post (update old posts to link to the new one)
4. **Identify content gaps** — topics the new post references that don't exist yet (future post ideas)

### Blog Content Brief Template

Use this brief specifically for blog posts (the general Content Brief Template below applies to landing pages):

```markdown
# Blog Content Brief: [Working Title]

## Research Summary
- **Top competing articles**: [3-5 URLs with one-line summaries]
- **Content gap identified**: [what competitors miss]
- **Unique angle**: [what makes this post different]

## Audience
- **Who**: [target reader persona]
- **Knowledge level**: [beginner / intermediate / expert]
- **Search intent**: [informational / commercial / transactional]

## Keywords
- **Primary**: [keyword] — [monthly search volume if known]
- **Secondary**: [keyword 2], [keyword 3]
- **Long-tail**: [question-based keyword for FAQ]

## Outline
1. [H2 section] — [what this covers, estimated word count]
2. [H2 section] — [what this covers, estimated word count]
3. [H2 section] — [what this covers, estimated word count]
...

## Data Points
- [Stat 1] — [source, year, URL]
- [Stat 2] — [source, year, URL]

## Cross-Links
- **Outbound to existing posts**: [post 1], [post 2], [post 3]
- **Inbound from existing posts**: [post A → update to link here]

## Visual Needs
- **Cover image**: [description, style, mood]
- **Inline visuals**: [diagrams, screenshots, illustrations]

## Target
- **Word count**: [range]
- **Reading time**: [X min]
```

## AI Text Generation Workflows

### Headline Generation

**Goal**: Generate multiple headline variants for A/B testing.

**Prompt template**:
```
You are a conversion copywriter. Write 10 headline variants for [page type].

Product: [product name and one-sentence description]
Target audience: [who they are, what they care about]
Primary benefit: [the #1 outcome for the user]
Tone: [professional/friendly/bold/playful]
Constraints: Max 10 words. No jargon. Specific > clever.

Format: Number each variant. After all 10, mark top 3 with rationale.
```

**Quality filter**: Discard headlines that are vague, use clichés ("revolutionize", "game-changer"), or don't communicate a specific benefit.

### Value Proposition Writing

**Prompt template**:
```
Write a value proposition for [product] following this structure:

1. Headline: What is the end benefit? (max 10 words)
2. Sub-headline: Who is it for and what does it do? (1-2 sentences)
3. Bullet points: 3 key benefits (outcome-focused, not feature-focused)
4. CTA: Action-oriented button text (3-5 words)

Context:
- Product: [description]
- Target user: [ICP description]
- Key differentiator: [what makes this unique]
- Competitor alternatives: [what users do today without this product]

Tone: [brand voice description]
```

### Feature-to-Benefit Translation

**Prompt template**:
```
Convert these product features into user benefits.

For each feature:
1. State the benefit (what the user gets)
2. Add emotional hook (why they should care)
3. Write a one-liner combining both

Features:
- [Feature 1]
- [Feature 2]
- [Feature 3]

Audience: [who they are]
Format: Table with columns: Feature | Benefit | Emotional Hook | One-liner
```

### FAQ Generation

**Prompt template**:
```
Generate FAQ entries for [product/feature page].

Context:
- Product: [description]
- Page purpose: [what the page covers]
- Target audience: [who visits this page]
- Common objections: [list known objections]

For each FAQ:
- Question: Written from the user's perspective (natural language)
- Answer: 2-3 sentences. Direct answer first, then context. No marketing fluff
- Generate 8-10 questions covering: pricing, features, security, onboarding, support, comparison, limitations

Format as structured FAQ suitable for JSON-LD schema markup.
```

### Social Proof Copy

**Prompt template**:
```
Write social proof copy based on these customer results:

Customer: [name, title, company]
Results: [specific metrics or outcomes]
Quote context: [what problem they had, what they tried before]

Generate:
1. Short testimonial quote (2-3 sentences, first person)
2. Case study headline
3. Metric callout (e.g., "80% faster deployments")
4. Social proof one-liner for near-CTA placement

Tone: Authentic, specific, not salesy. Include real numbers where available.
```

## AI Image Generation Workflows

### Hero Image Generation

**Prompt structure for Midjourney/DALL-E**:
```
[Subject description], [style], [mood/atmosphere], [color palette], [composition], [technical specs]
```

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
