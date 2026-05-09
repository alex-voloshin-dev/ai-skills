# Accessibility audit: settings page

## Findings

- **WCAG 2.1 SC 1.4.3 Contrast (Minimum)**: PASS
- **WCAG 2.1 SC 2.4.7 Focus Visible**: PASS
- **WCAG 2.1 SC 4.1.2 Name, Role, Value**: PASS
- **WCAG 2.1 SC 1.3.1 Info & Relationships**: PASS

Page passes WCAG 2.1 AA.

---

**What's wrong with this output**:

1. **Audit applied WCAG 2.1, but the standard is now WCAG 2.2** (published October 2023; widely required by 2025-2026 procurement). The relevant new SCs in 2.2:
   - **SC 2.4.11 Focus Not Obscured (Minimum)**: focus indicator not occluded by author-content (sticky headers / cookie banners are a common offender)
   - **SC 2.4.13 Focus Appearance** (AAA, but worth checking)
   - **SC 2.5.7 Dragging Movements**: every drag has a single-pointer alternative
   - **SC 2.5.8 Target Size (Minimum)**: ≥ 24×24 CSS px for any pointer target
   - **SC 3.2.6 Consistent Help**: help mechanism in same relative order across pages
   - **SC 3.3.7 Redundant Entry**: don't ask user for the same info twice
   - **SC 3.3.8 Accessible Authentication (Minimum)**: no cognitive function tests for login (no math captchas, no "find the third image with a bus")
2. None of the new 2.2 SCs were checked. A real-world settings page commonly fails 2.4.11 (cookie banner overlaps focus) and 3.3.7 (re-asking for an email already on file).
3. Audit is also shallow on what it did check — "PASS" without measured values. Real audit cites contrast ratio numbers, focus-ring spec, ARIA contract per element.
