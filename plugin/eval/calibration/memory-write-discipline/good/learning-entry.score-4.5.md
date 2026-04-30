# Memory Entry — Learned pattern

**Topic:** Node.js async error handling in event handlers

**Learned:** When registering async handlers with `.on('event', async (data) => {})`, unhandled rejections silently fail in older Node versions. Always wrap in try/catch or use `.catch()`.

**Evidence:** Debugging issue #4102 (webhook delivery failures). Root cause: async handler in `event-emitter` threw on invalid JSON, rejection wasn't logged. Confirmed behavior across Node 14, 16, 18.

**Project applicability:** Affects `src/webhook-handler.js` (event emitters on message bus) and any code using `.once()` with async functions.

**Action items:**
- [ ] Check existing event handlers for unhandled rejections (esp. `messagebus.on(...)`)
- [ ] Add ESLint rule: warn on `async` in event handler without explicit error handling
- [ ] Add test case for async handler rejection

**Confidence:** High. Replicated locally. Node.js docs confirm behavior.

**Related entries:** "Promise handling in callbacks" (2026-04-15), "Error propagation in worker threads" (2026-04-10)

