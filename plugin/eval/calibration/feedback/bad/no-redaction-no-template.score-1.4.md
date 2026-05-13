# /feedback — Output (verbose dump; no template; no redaction discipline)

> Invocation: `/feedback --plugin ai-assets`

Sessions scanned: 5. Found 3 errors:

1. session 89f51dcc — hook ralph-stop.py crashed with the full unredacted environment dump including credential-shaped values that were never masked, full home paths leaked, no normalization
2. session 9f877090 — assistant stop_reason=tool_use_error, payload included a value labelled like a token that the worker is supposed to mask but the report shows verbatim
3. session 415a353a — system error excerpt printed verbatim with no truncation, full file paths, no signature collapse

Done.

(no grouping; no signature normalization; no extended report path printed; no memory write performed; verdict missing entirely; brief and extended outputs do not follow the shared template; raw home-directory paths visible)
