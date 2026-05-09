# Security scan: rag-pipeline — escalating to /security-audit

## AI/LLM detection (Step 0)

```bash
$ grep -rE "anthropic|openai|langchain|llama_index|pinecone|weaviate" \
    pyproject.toml package.json 2>/dev/null
pyproject.toml:    "anthropic>=0.40.0"
pyproject.toml:    "langchain-core>=0.3"
pyproject.toml:    "pinecone-client>=4.1"
```

Three AI/LLM components detected: anthropic SDK, LangChain, Pinecone vector store.

## Recommendation: escalate

Per skill's boundary discipline, this scan alone is **insufficient**. The OWASP LLM Top 10 (2025) is not in scope for /security-scan; it is required for any project shipping LLM components.

→ **Run `/security-audit` after this scan completes.** The audit will cover:
- LLM01 prompt injection (direct + indirect via retrieved documents)
- LLM02 sensitive info disclosure
- LLM03 supply-chain (model + data poisoning paths)
- LLM05 improper output handling (XSS via LLM-generated HTML, SQL injection if outputs hit DB)
- LLM06 excessive agency (tool-call scope, side-effect risk)
- LLM07 system-prompt leakage
- LLM08 vector + embedding weaknesses (Pinecone-relevant)
- LLM10 unbounded consumption (rate limits, max_tokens caps)

## Step 2 results (still ran the standard scan)

```bash
$ osv-scanner --lockfile=poetry.lock
3 vulnerabilities. Highest EPSS 0.34 (medium tier). None KEV-listed.
```

## Step 3 (secrets)

```bash
$ gitleaks detect --source . --redact
0 leaks.
```

## Final report

- Standard scan: PASS (3 medium-EPSS deps to track)
- **AI/LLM components present** → escalate to `/security-audit`. Do not consider this scan sufficient for release.

## Score rationale

LLM detection (5), correct escalation per G3 boundary (5), still ran standard scan (4), report flagged the gap (4). Avg 4.2.
