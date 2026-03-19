# Privacy & Compliance for AI Systems

Patterns for building privacy-respecting, compliant AI systems. Covers multi-tenant isolation, organizational data controls, user consent, data residency, and regional compliance.

Based on `guides/context_engineering_guide.md` §9.

---

## Multi-Tenant Isolation

When agents operate over shared indexes for multiple tenants (users/orgs), retrieval can leak data across tenants without explicit isolation.

### Retrieval-Time Isolation (Required)

- **Filter every vector query by `tenant_id`** — namespace-based or metadata filter
- **Never retrieve documents outside the current tenant's namespace**, even if semantically relevant
- **Validate tenant filters server-side** — do not rely on the model to apply them
- **Test isolation**: query as Tenant A, verify zero results from Tenant B's namespace

### Memory Scoping

- Extend the memory `scope` field to include `tenant_id`:
  ```json
  {"scope": {"level": "project", "tenant_id": "org-abc", "user_id": "user-123"}}
  ```
- Memory items must never be retrieved cross-tenant
- Memory conflict resolution respects tenant boundaries (no cross-tenant overrides)

### Index Architecture

| Approach | Isolation Strength | Performance | Operational Cost |
|---|---|---|---|
| **Namespace-per-tenant** | Strong (physical separation) | Slightly slower (more indexes) | Higher (more indexes to manage) |
| **Filter-per-tenant** (shared namespace) | Moderate (metadata filter) | Faster (single index) | Lower, but requires strict metadata hygiene |

**Recommendation**: Namespace-per-tenant for regulated industries (finance, healthcare, government). Filter-per-tenant acceptable for lower-risk scenarios with strong metadata validation.

**Risk**: Corrupted metadata in filter-per-tenant can break isolation **silently** — no error, just wrong data returned. Add integrity checks.

---

## Organizational Data Controls

When agents operate over corporate data (docs, tickets, repos, Slack, email).

### Retrieval-Time Permission Checks

- **Never retrieve items the current user cannot access** — even if they exist in the vector index
- Implement permission checks at the retrieval layer, not the prompt layer
- Mirror source system permissions (e.g., if user can't access a Confluence page, don't retrieve it)
- Cache permission decisions with short TTL — permissions change

### Need-to-Know Packing

- **If a document is accessible but not necessary for the current task, don't include it** in context
- Apply relevance filtering AFTER permission filtering
- Don't pack context just because it's available — minimize data exposure

### Trace Access Control

- Restrict who can view traces — they contain sensitive corporate data (retrieved docs, user queries, model responses)
- Separate retention policies for corporate vs personal data in traces
- Role-based access: developers see sanitized traces, security team sees full traces
- Audit trail: log who accessed which traces and when

---

## Consent and User Controls

### Memory Disclosure

- **Disclose** whether content may be stored as memory and how it is used
- Explain at first interaction what types of data are remembered
- Provide clear opt-in/opt-out mechanisms

### Memory Review Pathway

Users must be able to:
- **View** all stored memories about them (structured, readable format)
- **Edit** incorrect memories (correct factual errors, update preferences)
- **Delete** specific memories or all memories
- **Export** their memory data (data portability)

### Right to Be Forgotten

Deletion must cover:
- **Raw records** — conversation logs, interaction history
- **Vector store embeddings** — delete source document AND corresponding embeddings
- **Memory items** — all structured memory entries
- **Derived data** — summaries, rollups, cached results that reference deleted data

**Note**: Deletion from model weights after fine-tuning is a harder problem. Avoid training on personal data unless you have a governed process with deletion capabilities.

### Consent Tracking

```json
{
  "user_id": "user-123",
  "tenant_id": "org-abc",
  "consents": {
    "memory_storage": {"granted": true, "timestamp": "2025-11-01T10:00:00Z"},
    "conversation_logging": {"granted": true, "timestamp": "2025-11-01T10:00:00Z"},
    "data_for_improvement": {"granted": false, "timestamp": "2025-11-01T10:00:00Z"}
  },
  "deletion_requests": []
}
```

---

## Data Residency

### Requirements Mapping

- Keep embeddings, caches, and logs in the **required region**
- Ensure AI/LLM vendors can honor region pinning (not all do)
- Map each data type to its residency requirement:

| Data Type | Example | Residency Requirement |
|---|---|---|
| Vector embeddings | Document chunks in Pinecone/Weaviate | Must match source data residency |
| Inference logs | Prompts + model responses | Potentially personal data — region-pin |
| Memory store | User preferences, facts | User's home region |
| Traces | Full interaction traces | Most restrictive of all data involved |
| Model cache | KV cache, prefix cache | Same region as inference |

### Vendor Assessment

Before selecting AI infrastructure:
- [ ] Vendor supports region-pinned inference (data doesn't leave region)
- [ ] Vendor supports region-pinned storage (embeddings, logs, cache)
- [ ] Vendor provides data processing agreements (DPA) for required jurisdictions
- [ ] Vendor deletion API covers all stored data (not just primary records)
- [ ] Vendor doesn't use customer data for training without explicit opt-in

---

## Inference Logging

Treat prompts, model outputs, and tool traces as **potentially personal data**.

### Minimization

- Log only what's needed for debugging and evaluation
- Redact PII before logging (names, emails, phone numbers, addresses)
- Don't log full retrieved documents — log doc_ids and relevance scores instead
- Don't log full model responses in production — log structured outputs and metrics

### Retention Policies

| Data Type | Suggested Retention | Notes |
|---|---|---|
| Full traces (debug) | 7-30 days | Auto-delete, restricted access |
| Anonymized metrics | 90-365 days | For evaluation and monitoring |
| Audit logs | Per compliance requirement | Often 1-7 years for regulated industries |
| Memory items | Until user deletion or TTL | User-controlled |

### Access Control

- RBAC for trace access — not everyone needs to see full traces
- Purpose separation: debugging traces ≠ evaluation data ≠ compliance audit
- Log access to traces themselves (who viewed what, when)

---

## Regional Compliance Notes

### EU / GDPR

Build with **privacy-by-design**:
- **Data minimization**: Retrieve/store only what you need for the task
- **Purpose limitation**: Separate memory by purpose (support ≠ billing ≠ personalization). Don't reuse data across purposes without consent
- **Transparency**: Log what was retrieved and why. Users can request this log
- **Retention controls**: TTL policies on all data types. User-driven deletion
- **Data Protection Impact Assessment (DPIA)**: Required for high-risk AI processing

### California / CCPA

- Right to know what personal data is collected
- Right to delete personal data
- Right to opt-out of sale/sharing of personal data
- Businesses must disclose AI use in decision-making

### Canada / PIPEDA

- Consent required for collection, use, and disclosure of personal information
- Purpose must be identified at or before time of collection
- Individual access to their personal information on request

### General Principles (All Jurisdictions)

- **Minimize**: Collect and store the minimum data necessary
- **Purpose-limit**: Use data only for stated purposes
- **Secure**: Encrypt at rest and in transit. Access controls
- **Transparent**: Tell users what you collect, why, and how long
- **Deletable**: Provide deletion mechanisms across all storage layers
- **Auditable**: Log data flows for compliance verification

---

## Implementation Checklist

→ See also: `production-checklists.md` §8 (Privacy & Compliance Checklist) for the full production gate checklist.

Quick implementation checklist for AI privacy:

- [ ] Tenant isolation: server-side filtering on every vector query
- [ ] Memory scoping: `tenant_id` + `user_id` in all memory operations
- [ ] Permission checks: retrieval respects source system access controls
- [ ] Consent tracking: user opt-in/opt-out recorded and enforced
- [ ] Memory review: user can view, edit, delete their memories
- [ ] PII redaction: applied before logging and storage
- [ ] Data residency: mapped per data type, vendor capabilities verified
- [ ] Retention policies: defined per data type, automated enforcement
- [ ] Trace access: RBAC enforced, access logged
- [ ] Deletion pathway: covers raw records + embeddings + memories + derived data
