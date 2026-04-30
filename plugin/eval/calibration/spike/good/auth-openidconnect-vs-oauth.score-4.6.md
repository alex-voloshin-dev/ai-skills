# Spike — Should we add OpenID Connect support alongside OAuth2?

## Question
Can we integrate OpenID Connect as a second authentication provider within 4 weeks, and will it reduce custom auth code in integrations by ≥ 30%?

## Time Cap: 120 min (used: 95 min)

## Findings

### Integration complexity (POC on 2 real customers)
- Customer A (uses Okta OIDC): standard library integration (authlib + oidc-provider); 3 hours to connect
- Customer B (uses Auth0): same library stack; 2.5 hours; reused 85% of setup from Customer A
- **Current OAuth2-only requirement:** custom JWT validation + user attribute mapping for each tenant — ~5 hours per customer

### Code reduction measurement
- Current custom code per OAuth customer: ~200 lines (JWT parsing, attribute extraction, role mapping)
- OIDC-native library handling same: ~40 lines (relying on ID token, standard claims)
- **Reduction: 80%** — exceeds the 30% target

### Library assessment
- authlib (Python): mature, OIDC support stable; 2.8M weekly downloads; MIT license
- Maintains compatibility with existing OAuth2 clients
- OpenID Connect Discovery supported (auto-config for customer endpoints)

### Migration effort estimate
- Library integration + test harness: 3 engineer-days
- Retrofit 2 existing OAuth customers to OIDC (optional, backward-compat mode): 2 ed per customer
- Documentation + runbook: 1 ed
- **Total for library + dual-mode:** 6 ed (within 4-week window, no blockers)

## Trade-offs Considered

| Option | Code reduction | Effort | Risk | Deployment |
|---|---|---|---|---|
| Status quo (OAuth2 only) | 0% | 0 | low | none |
| **Add OIDC support (dual-mode)** | 80% | 6 ed | low | simple |
| Build custom OIDC handler | 75% | 12 ed | medium | complex |
| Switch exclusively to OIDC | 80% | 10 ed (migrate all customers) | high | requires migration |

OIDC library is lowest-effort path to target reduction.

## Recommendation

**GO — add OIDC dual-mode support.** Library matures ecosystem, reduces custom code, maintains backward compatibility. No risk to existing OAuth2 customers.

## Next Steps

- **Week 1:** integrate authlib OIDC; add test for Customer A scenario
- **Week 2:** beta test with Customer A; document setup; gather feedback
- **Week 3:** refine based on feedback; add 1 more customer (Customer B validation)
- **Week 4:** documentation + runbook; announce to sales + customer success
- **Owner:** identity-team
- **Decision deadline:** end of Week 2 (if both customers report success, no gate; if issues, re-spike library alternatives)
- **Criteria for revisit:** if authlib compatibility breaks on any tier → fallback to custom handler

## POC artifacts
- `spike-oidc-poc-2026-04-21/authlib-integration/` — minimal OIDC provider (Okta + Auth0)
- Test results: `spike-oidc-poc-2026-04-21/test-results.log`
