# Social Media Manager Rubric

## Overview

Rubric for `social-media-manager` outputs (X/Twitter, LinkedIn posts + newsletters, Facebook, Threads, Bluesky). Measures platform-fit, hook quality, zero-click compliance, engagement-pattern usage, hashtag discipline, and humanizer pass. Grounded in `plugin/skills/social-media-manager/SKILL.md`.

## Dimensions

### Dimension 1: Platform-Fit
Matches the platform's character limit and format conventions.

| Platform | Limit |
|---|---|
| X / Twitter (post and thread reply) | ≤ 280 |
| LinkedIn post | 1,300–1,900 sweet spot |
| LinkedIn newsletter | up to ~100,000 |
| Facebook | < 1,000 |
| Threads | ≤ 500 |
| Bluesky | ≤ 300 |

- **Level 1:** Hard-limit violation (over-character or truncated)
- **Level 2:** Within hard limit; ignores sweet-spot guidance (LinkedIn under 1,300 or over 1,900)
- **Level 3:** Within sweet spot; format conventions ignored
- **Level 4:** Within sweet spot + platform format applied (LinkedIn line breaks, X thread numbering, Bluesky starter-pack note)
- **Level 5:** All of L4 + platform-specific surface used (Bluesky AT-Protocol starter-pack, LinkedIn newsletter cadence, X reply-as-link)

### Dimension 2: Hook Quality
First line / first sentence works as a standalone hook. No preamble, no generic topic intro.

- **Level 1:** Generic opener ("In this post we'll explore…", "Today I want to talk about…")
- **Level 2:** Topic-led ("Customer churn matters") rather than insight-led
- **Level 3:** Concrete but flat ("We tested 5 SaaS landing pages")
- **Level 4:** Specific finding or surprising stat as the hook
- **Level 5:** All of L4 + tension or stakes embedded in the hook ("Your landing page leaks 40% of warm leads in the first 8 seconds")

### Dimension 3: Zero-Click Compliance
Value embedded in the post body. Reader gets the insight without clicking. Domain mentioned plain-text (no hyperlink penalty). Link, if any, in last reply (X) or "link in profile" (LinkedIn).

- **Level 1:** Hyperlink in main body forcing click for value
- **Level 2:** Tease + link; no standalone value
- **Level 3:** Some value embedded; primary insight still gated behind click
- **Level 4:** Full insight embedded; link only as "deep dive" reference
- **Level 5:** All of L4 + plain-text domain mention + link relegated to last reply / profile

### Dimension 4: Engagement-Pattern Usage
Uses platform-appropriate engagement levers: open-ended question for replies, conversation-prompt at thread end (X reply weight is heavy), poll where natural, specific (not generic) call to discuss.

- **Level 1:** No engagement prompt; statement-only post
- **Level 2:** Generic CTA ("thoughts?", "agree?")
- **Level 3:** Specific question but no opinion stake to react to
- **Level 4:** Specific question + opinion stake + matches platform's engagement weight (X thread T8 conversation prompt, LinkedIn carousel close-out)
- **Level 5:** All of L4 + first-person stakes ("we tested" / "I checked") to invite peer-level reply

### Dimension 5: Hashtag Discipline
Per `references/platform-guide.md`: 0–2 max on X; 3–5 CamelCase on LinkedIn; none on Threads/Bluesky; sparing on Facebook.

- **Level 1:** Hashtag spam (5+ on X, 10+ on LinkedIn, any on Threads/Bluesky)
- **Level 2:** Over budget by one (3 on X, 6 on LinkedIn)
- **Level 3:** At budget but not CamelCase on LinkedIn or relevance weak
- **Level 4:** Within budget + CamelCase on LinkedIn + relevant to ICP
- **Level 5:** All of L4 + hashtag drives discoverability evidence (community tag) rather than category tag

### Dimension 6: Humanizer Pass
Runs `@humanizer` skill. Varied sentence rhythm; no AI tells (em-dash overuse, rule of three, "delve", "landscape", "It's not just X, it's Y"); first-person voice; concrete stakes.

- **Level 1:** Multiple AI tells; reads like a brand broadcast bot
- **Level 2:** Some AI vocabulary; rhythm uniform
- **Level 3:** Mostly clean; one or two artefacts
- **Level 4:** No AI vocabulary; varied rhythm; first-person voice
- **Level 5:** All of L4 + concrete imagery + reads aloud well + sounds like a person sharing an observation, not a brand

## Scoring Logic

- **Aggregate:** average of D1–D6
- **Pass threshold:** 4.0
- **Judge model:** Haiku (pattern matching: char count, hashtag count, AI tells)

## Anti-Patterns (Auto-Fail)

- Same body copy posted across X / LinkedIn / Threads / Bluesky without per-platform adaptation
- LinkedIn post over 4,000 chars (algorithmic dampening past sweet-spot ceiling)
- 5+ hashtags on a 280-char tweet
- Hyperlink as the primary CTA in the main body of a 2026 platform post
- Generic engagement closer ("thoughts?") with no opinion stake
- Posted from company page when team-member personal account was available

## Calibration Reference

- **Known-good:** `plugin/eval/calibration/social-media-manager/good/*`
- **Known-bad:** `plugin/eval/calibration/social-media-manager/bad/*`
