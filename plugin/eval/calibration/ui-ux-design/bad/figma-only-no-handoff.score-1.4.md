# Design output: New checkout flow

## Deliverables

- Figma file: https://www.figma.com/file/abc123/Checkout-Flow-2026 ✓
- 12 frames covering all screens of the new flow ✓
- Components used from the design system ✓

That's it — handoff to engineering can pick this up.

---

**What's wrong with this output**:

1. **No handoff document**. The skill ships `assets/handoff-template.md` precisely so engineers receive: component inventory, design tokens used per component, accessibility requirements, animations / `prefers-reduced-motion` fallbacks, edge cases (empty / loading / error / overflow / RTL), browser matrix, gotchas. None of that was produced. The engineer will have to inspect every frame in Figma and infer everything.
2. **No accessibility spec**. WCAG 2.2 SC checks not enumerated per component. Focus order not specified. Keyboard interactions not described. ARIA contracts undocumented. The "12 frames" cover happy path only.
3. **No states**. Real spec has default / hover / focus / active / disabled / loading / error per interactive element. Frames in Figma typically have 1-2 states; engineer has to either invent the rest or come back asking.
4. **No edge cases**. What happens with a 47-character street name? With RTL languages? Empty cart? Network failure during checkout? None visible in the frames.
5. **No browser/device matrix**. What's the mobile breakpoint behaviour? Does it support older Safari? Edge cases in iOS Safari that affect input focus? Silent.
6. **"Components used from the design system"** is unverifiable. Without a checklist (token names cited per usage), engineer can't confirm — and any drift won't be caught.

Result: engineer either ships an incomplete checkout, OR holds the work for two weeks of clarifying Q&A.
