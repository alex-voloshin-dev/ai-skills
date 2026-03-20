---
trigger: agent
description: Enforce humanizer pass on all public-facing text — blog posts, social media posts, UI copy, microcopy, emails, landing pages, marketing content, newsletters, documentation for external users. Activates when writing, editing, or reviewing any content intended for publication or end-user display.
---

# Humanize All Published Content

Every piece of text intended for publication or end-user display MUST pass through the `@humanizer` skill before finalization.

## Scope

This rule applies to:
- Blog posts and articles
- Social media posts (X/Twitter, LinkedIn, Reddit, any platform)
- UI copy and microcopy (buttons, tooltips, error messages, onboarding flows, empty states)
- Email campaigns and newsletters
- Landing page copy
- Marketing materials
- Public-facing documentation
- Release announcements
- Product descriptions

This rule does NOT apply to:
- Internal technical documentation (ADRs, design docs, internal READMEs)
- Code comments and docstrings
- Commit messages and PR descriptions
- Configuration files
- AI asset files (rules, skills, workflows)

## Requirements

1. **Always run the humanizer pass** — after writing any public-facing text, apply `@humanizer` skill patterns before presenting to the user
2. **Write human from the start** — do not write AI-sounding text and then fix it. Internalize the patterns and avoid them during initial drafting
3. **Anti-AI audit is mandatory** — for any text longer than 2 paragraphs, perform the "What makes this obviously AI generated?" self-check before finalizing
4. **Preserve intent and accuracy** — humanizing never means making content less accurate or less useful. Remove AI-isms, keep substance
5. **Match the voice** — different contexts need different tones. A blog post can be informal; UI copy should be concise and clear; marketing emails can have personality

## Key Patterns to Avoid (always)

- AI vocabulary: additionally, delve, foster, garner, intricate, landscape, tapestry, underscore, vibrant, pivotal, crucial
- Promotional inflation: nestled, groundbreaking, stunning, breathtaking, renowned
- Chatbot artifacts: I hope this helps, Certainly!, Would you like...
- Sycophantic tone: Great question!, You're absolutely right!
- Em dash overuse, emoji decoration, bold-header lists
- Rule of three, negative parallelisms, false ranges
- Generic positive conclusions: the future looks bright, exciting times ahead
- Filler: in order to, due to the fact that, it is important to note
