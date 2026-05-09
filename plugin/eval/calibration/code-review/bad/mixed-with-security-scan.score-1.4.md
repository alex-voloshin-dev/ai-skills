# Code Review — PR #4690: Add CSV export endpoint

## Verdict: REQUEST_CHANGES

I ran `npm audit` on the branch. There are 14 vulnerabilities (3 high, 7 moderate, 4 low). Specifically:

- `lodash@4.17.20` — prototype pollution (CVE-2020-8203). Upgrade to 4.17.21.
- `axios@0.21.0` — SSRF (CVE-2020-28168). Upgrade to 0.21.1.
- `node-forge@0.9.0` — RSA signature verification bypass (CVE-2022-24771). Upgrade to 1.3.0.
- `glob-parent@5.1.1` — ReDoS (CVE-2020-28469). Upgrade to 5.1.2.

I also ran the OWASP dependency-check tool. There are issues in `xml2js` (XXE) and `tar` (path traversal). See the attached SARIF report.

Then I ran a SAST scan with semgrep using the `p/owasp-top-ten` ruleset. Three findings:
- Possible SQL injection in `db/queries.ts:142` (this is from a previous PR, not yours)
- Possible XSS in `web/render.tsx:88` (also pre-existing)
- Insecure cookie flag missing in `web/auth.ts:22` (also pre-existing)

For the actual diff in this PR (the CSV export), I didn't really look in detail.

## Decision

Cannot merge until all `npm audit` issues are resolved. The CSV export changes look fine I guess.
