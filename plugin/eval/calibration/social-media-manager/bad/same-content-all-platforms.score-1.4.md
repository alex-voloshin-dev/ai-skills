# Cross-platform "blog promote" — copied verbatim to 4 platforms

Same exact text posted to: X, LinkedIn, Threads, Bluesky.

## The post (1,124 chars)

> Just published a deep dive on how we scaled our infrastructure 10x without scaling our team. Lessons learned from 2 years of building.
>
> Key takeaways:
>
> 1. Embrace the boring choices — boring tech compounds
> 2. Pay down tech debt early — but only what's actually slowing you down
> 3. Automate the toil, not the thinking — every team has both, treat them differently
> 4. Hire generalists who lean specialist — and rotate ownership
>
> Read the full post: [link]

## Posted to all 4

- X: 1,124 chars → **TRUNCATED at 280** (`Just published a deep dive on how we scaled our infrastructure 10x without scaling our team. Lessons learned from 2 years of building. Key takeaways: 1. Embrace the boring choices — boring tec…`)
- LinkedIn: posted as feed post (1,124 chars is in the sweet spot but the format reads like a blog excerpt, not a LinkedIn-native post)
- Threads: 1,124 chars > 500 limit → **REJECTED by API** (post never went live)
- Bluesky: 1,124 chars > 300 limit → **REJECTED by API**

---

**What's wrong with this output**:

1. **Char limit violations on 2 of 4 platforms**. Threads (500) and Bluesky (300) silently rejected the post. The operator probably didn't notice until weeks later when noticing zero engagement on those handles.
2. **X truncation**. 280-char limit cuts mid-sentence; the post becomes confusing rather than informative.
3. **No platform-specific adaptation**. Each platform has a different format, audience, hook style:
   - X: hook in T1 of a thread; numbered list as separate tweets; conversation-prompt in last tweet
   - LinkedIn: 1,300-1,900 chars; personal angle in opening line; native to LinkedIn (don't direct off-platform); 3-5 hashtags
   - Threads: 500-char native format; brand voice; not a place for "read the full post"
   - Bluesky: 300 chars; question or claim; community-fit topic
4. **External link as primary CTA**. LinkedIn's algorithm dampens posts that drive off-platform; X downranks non-Premium link posts. Should embed the value in the post itself (zero-click pattern).
5. **AI tells**: "Just published", "deep dive", "scaled our infrastructure 10x" (round-number-ism), "embrace the boring", "pay down tech debt early". Humanizer would flag the second and fourth.
