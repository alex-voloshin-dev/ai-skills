# Non-Functional Requirements

| Category | Requirement |
|---|---|
| Performance | The system should be fast and responsive |
| Scalability | Should handle growth |
| Availability | Should be highly available |
| Security | Should be secure, follow best practices |
| Compliance | Should be compliant |
| Operability | Should be easy to operate |
| Cost | Should be cost-effective |

## Notes

The system should meet the needs of users and the business. We'll measure these as we go and tune based on what we learn in production.

---

**What's wrong with this output**: Every row is aspirational, not measurable. Real NFRs require quantified targets ("p99 < 250ms at 5k req/s", "RTO 15min / RPO 5min", "99.95% monthly availability with 21min/month error budget"). The expected output uses the `assets/nfr-template.md` table with the Specific Requirement / Measurement / Target Value / Source columns populated. Without numbers, no one can verify whether the system meets the NFR; it becomes folklore. Compliance row is especially hollow — should name SOC 2 / HIPAA / GDPR / PCI-DSS scope explicitly with control mappings.
