# Humanizer Compliance Rubric

## Overview

Cross-cutting rubric: text-facing output passes the `humanize-content` rule. Applied to feature-design, develop, bugfix, docs-pack, spike, marketing, content-creation outputs that include user-visible text.

## Dimensions

### Dimension 1: AI Vocabulary Absence
No high-frequency AI words: delve, foster, garner, intricate, landscape, tapestry, underscore, vibrant, pivotal, crucial, additionally.

- **Level 1:** Multiple AI vocabulary words; obviously AI-generated
- **Level 2:** Some AI vocabulary; reads as AI
- **Level 3:** Few AI vocabulary words; mostly natural
- **Level 4:** No AI vocabulary words
- **Level 5:** No AI vocabulary words AND no other AI tells (em-dash overuse, rule of three)

### Dimension 2: Sycophancy / Chatbot Artifact Absence
No "Great question!", "I hope this helps", "Certainly!", "I'm excited to", "I'm humbled to".

- **Level 1:** Multiple sycophantic / chatbot openers or closers
- **Level 2:** One or two
- **Level 3:** None of the obvious ones; a touch of "I'd be happy to" lingers
- **Level 4:** None; voice is direct
- **Level 5:** None + voice has personality without artifice

### Dimension 3: Natural Phrasing
Reads as if a competent human wrote it (no inflated symbolism, no superficial -ing analyses, no negative parallelisms).

- **Level 1:** Reads obviously AI; multiple inflated phrases ("It's not just X, it's Y")
- **Level 2:** Some inflated phrases
- **Level 3:** Mostly natural; one or two artifacts
- **Level 4:** Natural throughout
- **Level 5:** Natural + sentence variety + concrete imagery + reads aloud well

## Scoring Logic

- **Aggregate:** average of D1–D3
- **Pass threshold:** 4.0
- **Judge model:** Haiku (pattern matching is fast and cheap)

## Anti-Patterns (Auto-Fail)

- Em-dashes used as rhythm device 5+ times in 500 words
- Bold-emphasis used as a structural list ("**Key**: thing")
- Three-item rhetorical lists with rhythmic parallelism in successive sentences
- "Generic positive conclusion" pattern (the future looks bright, exciting times ahead)
- "It is important to note that…" filler

## Calibration Reference

- **Known-good:** `plugin/eval/calibration/humanizer-compliance/good/*`
- **Known-bad:** `plugin/eval/calibration/humanizer-compliance/bad/*`
