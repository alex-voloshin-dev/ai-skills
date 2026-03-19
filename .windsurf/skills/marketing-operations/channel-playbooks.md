# Channel Playbooks

Platform-specific best practices for marketing channels. Used by the `/marketing` workflow (Phase 2: Execute) for social media posts, email campaigns, and community engagement.

## X/Twitter Playbook

### Post Format

- **Character limit**: 280 characters (threads for longer content)
- **Hook**: First line must stop the scroll — bold claim, surprising stat, provocative question, or contrarian take
- **Structure**: Hook → Context → Insight → CTA (or thread teaser)
- **Hashtags**: 1-3 maximum, relevant to topic, placed at end
- **Media**: Images increase engagement 2-3x. Use screenshots, diagrams, or AI-generated visuals
- **Threads**: First tweet is the hook. Each tweet delivers one idea. End with summary + CTA

### Content Types (ranked by engagement)

| Type | Example | Best For |
|---|---|---|
| **Hot takes / opinions** | "Unpopular opinion: [contrarian view about industry]" | Engagement, followers |
| **Tips and how-tos** | "5 ways to [solve common problem]:" (thread) | Value, saves, shares |
| **Build in public** | "Just shipped [feature]. Here's what I learned:" | Authenticity, community |
| **Data and insights** | "We analyzed [X]. Here's what we found:" | Authority, shares |
| **Product updates** | "New: [feature] — [benefit in one line]" | Awareness, signups |
| **Curated content** | "Best [topic] resources I found this week:" | Value, followers |
| **Engagement posts** | "What's your biggest challenge with [topic]?" | Community, research |

### Posting Strategy

- **Frequency**: 1-3 posts/day (quality over quantity)
- **Best times**: 8-10 AM, 12-1 PM, 5-7 PM (audience timezone)
- **Engagement rule**: For every promotional post, create 4 value posts (80/20 rule)
- **Reply and engage**: Respond to comments within 2 hours. Quote-tweet interesting takes
- **Avoid**: Pure self-promotion, engagement bait, controversial politics, thread-only accounts

### Thread Structure

```
Tweet 1: Hook — bold claim or promise (this is 80% of the thread's success)
Tweet 2: Context — why this matters, who should care
Tweet 3-N: Main content — one insight per tweet, use numbered lists
Tweet N+1: Summary — key takeaways in bullet points
Tweet N+2: CTA — "Follow for more [topic]" or "Try [product] — [link]"
```

---

## LinkedIn Playbook

### Post Format

- **Length**: 150-300 words (sweet spot for engagement)
- **Hook**: First 2 lines visible before "see more" — must compel the click
- **Structure**: Hook → Story/insight → Lesson → CTA
- **Hashtags**: 3-5, placed at the end, mix of broad (#marketing) and niche (#B2BSaaS)
- **Formatting**: Short paragraphs (1-2 sentences), line breaks between paragraphs, bullet points for lists
- **Tone**: Professional but personal. First-person perspective. Share learnings, not lectures

### Content Types

| Type | Example | Best For |
|---|---|---|
| **Lessons learned** | "I made this mistake with [topic]. Here's what I'd do differently:" | Engagement, trust |
| **Industry insights** | "3 trends reshaping [industry] in 2025:" | Authority, shares |
| **Behind the scenes** | "Here's how we built [feature] and what surprised us:" | Authenticity |
| **Contrarian takes** | "Everyone says [common belief]. Here's why I disagree:" | Engagement |
| **How-to guides** | "Step-by-step: How to [achieve outcome]" | Saves, shares |
| **Celebrating milestones** | "We just hit [milestone]. Here's the journey:" | Community |

### Posting Strategy

- **Frequency**: 3-5 posts/week
- **Best times**: Tuesday-Thursday, 8-10 AM (business hours)
- **Engagement**: Comment on 5-10 relevant posts before/after your own post
- **Avoid**: Humble-bragging, "I'm humbled to announce", corporate jargon, engagement pods

---

## Reddit Playbook

### Core Rules

1. **Value first, always**: Reddit communities punish self-promotion. Provide genuine value
2. **Know the subreddit**: Read rules, lurk for a week, understand culture before posting
3. **Be authentic**: Redditors detect marketing speak instantly. Be direct and honest
4. **Disclose affiliation**: If sharing your own product, disclose: "Disclosure: I built this"

### Engagement Strategy

- **Comment on existing threads**: Answer questions related to your domain. Be helpful without mentioning your product
- **Share knowledge posts**: How-to guides, analysis, data — with no product mention
- **Ask for feedback**: Post in relevant subreddits asking for genuine feedback on your product
- **AMA**: If you have domain expertise, do an AMA in a relevant subreddit

### Relevant Subreddits by Audience

| Audience | Subreddits |
|---|---|
| Developers | r/programming, r/webdev, r/selfhosted, r/devops, r/sideproject |
| Startups | r/startups, r/SaaS, r/Entrepreneur, r/indiehackers |
| Product | r/ProductManagement, r/userexperience |
| Marketing | r/marketing, r/digital_marketing, r/SEO, r/content_marketing |
| AI/ML | r/artificial, r/MachineLearning, r/LocalLLaMA |

### Avoid

- Direct product links in posts (unless subreddit allows)
- Multiple posts in short time (looks like spam)
- Commenting only to promote (check your comment history ratio)
- Arguing with negative feedback

---

## Email Marketing Playbook

### Email Types

| Type | Purpose | Frequency | Key Metric |
|---|---|---|---|
| **Newsletter** | Value delivery, relationship building | Bi-weekly or weekly | Open rate, click rate |
| **Product update** | Announce features, improvements | Per release | Click rate, feature adoption |
| **Welcome sequence** | Onboard new subscribers | Automated (3-5 emails) | Activation rate |
| **Nurture sequence** | Move leads toward conversion | Automated | Conversion rate |
| **Re-engagement** | Win back inactive subscribers | Triggered | Reactivation rate |

### Newsletter Structure

```
Subject line: [Specific benefit or curiosity hook] — 3 variants for A/B test
Preview text: [Expands on subject, doesn't repeat it]

---

Opening: Personal note or hook (2-3 sentences)

Section 1: Main value content (tip, insight, tutorial)
  - Actionable, not just informational
  - Include one visual (screenshot, diagram)

Section 2: Secondary content (curated links, industry news)
  - 3-5 items with one-line descriptions

Section 3: Product update or CTA (if applicable)
  - Soft sell, value-framed: "We built X to help you Y"

Closing: Personal sign-off, invite replies

Footer: Unsubscribe, preferences, social links
```

### Subject Line Formulas

| Formula | Example |
|---|---|
| **Number + benefit** | "5 ways to reduce deploy time by 80%" |
| **How to + outcome** | "How to automate your CI pipeline in 10 minutes" |
| **Question** | "Are you still doing deployments manually?" |
| **Curiosity gap** | "The mistake most DevOps teams make (and how to fix it)" |
| **News/update** | "New: [Feature] — [one-line benefit]" |
| **Personal** | "I broke production last week. Here's what I learned." |

### Best Practices

- **Send time**: Tuesday-Thursday, 9-11 AM (subscriber timezone)
- **Frequency**: Consistent cadence > high frequency. Never send daily unless subscriber opted in
- **Personalization**: Use first name, segment by interest/behavior
- **Mobile**: 60%+ opens on mobile. Short subject lines (≤50 chars), scannable body, large CTA buttons
- **Metrics targets**: Open rate >25%, click rate >3%, unsubscribe <0.5%

---

## Community Engagement Playbook

### Platforms

- **Discord / Slack**: Join communities where your ICP hangs out. Help without selling
- **Hacker News**: Comment on relevant Show HN posts. Submit your own Show HN at launch
- **Stack Overflow**: Answer questions in your domain. Link to docs (not product) when relevant
- **GitHub Discussions**: Engage with open source projects related to your product
- **Forums**: Industry-specific forums (e.g., IndieHackers for bootstrappers)

### Engagement Protocol

1. **Listen first**: Spend 1 week observing before actively participating
2. **Help genuinely**: Answer questions based on expertise, not product features
3. **Build reputation**: Consistent helpful contributions over weeks/months build trust
4. **Share sparingly**: Only share your product when directly relevant and helpful
5. **Track conversations**: Monitor mentions of your product, competitors, and key topics

### Daily Engagement Routine (15-30 min)

1. Check mentions and notifications (5 min)
2. Find 2-3 relevant questions/discussions to contribute to (10 min)
3. Post one valuable comment or insight (5 min)
4. Note content ideas from community questions (5 min)

---

## Trend Research Playbook

### Sources

| Source | What to Look For | Frequency |
|---|---|---|
| **X/Twitter** | Trending hashtags, viral threads in your niche, competitor posts | Daily |
| **Hacker News** | Front page topics, Show HN launches, comment sentiment | Daily |
| **Reddit** | Top posts in relevant subreddits, recurring questions | 2-3x/week |
| **Google Trends** | Rising search terms, seasonal patterns | Weekly |
| **Industry newsletters** | Expert opinions, market shifts, new tools | As received |
| **Competitor blogs** | New content, positioning changes, feature announcements | Weekly |
| **Product Hunt** | Trending launches in your category, competitor launches | 2-3x/week |

### Research Output Template

```markdown
# Trend Research — [YYYY-MM-DD]

## Key Findings

### Trend 1: [title]
- **Source**: [where you found it]
- **Signal strength**: [weak / moderate / strong]
- **Relevance to us**: [how it connects to our product/audience]
- **Content opportunity**: [post idea, angle, format]
- **Urgency**: [time-sensitive / evergreen]

### Trend 2: [title]
...

## Competitor Activity
- [Competitor A]: [what they did, our response]
- [Competitor B]: [what they did, our response]

## Content Ideas Generated
1. [idea] — [channel] — [pillar] — [priority]
2. [idea] — [channel] — [pillar] — [priority]

## Community Signals
- [recurring question or pain point observed]
- [sentiment shift about topic/competitor]
```

### Analysis Framework

For each trend, evaluate:

1. **Relevance**: Does it connect to our product, audience, or content pillars?
2. **Timeliness**: Is this time-sensitive or evergreen?
3. **Angle**: What unique perspective can we add? (Don't just repeat)
4. **Format**: Best format to cover this? (Post, thread, blog, video)
5. **Effort**: Quick reaction post or deep-dive content?
