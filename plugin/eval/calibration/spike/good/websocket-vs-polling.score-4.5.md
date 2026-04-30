# Spike — Should we use WebSockets for real-time notifications instead of polling?

## Question
Would WebSockets reduce notification delivery latency from current 5-15s (polling interval) to < 1s, and what's the server cost impact?

## Time Cap: 120 min (used: 105 min)

## Findings

### Latency benchmark (staging with production data + client load)
- Current polling (30s interval): median 8s latency, p99 27s
- WebSocket POC: median 140ms latency, p99 380ms
- **Improvement: 57× faster median, 71× faster p99** — far exceeds < 1s target

### Server cost analysis
- Current polling: 400 clients × 2 polls/min = 800 req/min = 13 req/sec load
- WebSocket active connections: 400 clients × 1 persistent conn = 400 TCP connections
- Memory per WebSocket: ~8KB (protocol buffers + connection state) = 3.2MB total
- **Polling server cost:** CPU cost = ~60 mW (database + HTTP overhead)
- **WebSocket server cost:** CPU cost = ~30 mW (fewer DB queries) + memory = 3.2MB
- Net: slightly lower CPU, small memory cost (acceptable)

### Operational complexity
- Connection management: auto-reconnect on client side (library available: socket.io)
- Server-side: need heartbeat (keep-alives every 30s) to detect stale connections
- Backward compatibility: polling still works; can run dual-mode

### Effort estimate
- Server-side WebSocket handler + heartbeat: 3 ed
- Client-side integration (socket.io): 1 ed
- Testing (concurrent connections, failover, mobile): 2 ed
- Documentation: 1 ed
- **Total: 7 ed** (fits in 2-week sprint)
- Confidence: high (team has socket.io experience)

## Trade-offs Considered

| Option | Latency | CPU | Effort | Complexity |
|---|---|---|---|---|
| Status quo (polling 30s) | 8s p50, 27s p99 | 60 mW | 0 | simple |
| **WebSocket (persistent)** | 140ms p50, 380ms p99 | 30 mW | 7 ed | moderate |
| Polling faster (5s interval) | 2.5s p50, 8s p99 | 240 mW | 1 ed | simple |
| Webhook push (via providers) | < 100ms | varies | 15 ed | complex |

WebSockets offer best latency/effort trade-off. Polling at 5s interval is cheaper but still slow.

## Recommendation

**GO — implement WebSocket dual-mode.** Significantly improves UX with manageable effort. Server cost is slightly lower; operational risk is moderate but mitigable with heartbeat + client reconnect.

## Next Steps

- **Week 1:** implement server WebSocket handler + heartbeat; write load test
- **Week 2:** integrate socket.io client; test on 5 real browsers (Chrome, Safari, Firefox, Edge, mobile Safari)
- **Week 3:** dual-mode deployment (serve polling + WebSocket, allow client to choose)
- **Week 4:** monitor connection stability; iterate if issues
- **Owner:** realtime-team
- **Decision deadline:** end of Week 2 (load test + browser compat complete)
- **Criteria for revisit:** if p99 latency exceeds 500ms under 1000 concurrent connections → re-spike Webhook push option

## POC artifacts
- `spike-ws-poc-2026-04-21/server/` — WebSocket handler + heartbeat
- `spike-ws-poc-2026-04-21/client/` — socket.io integration (Vue.js)
- Load test: `spike-ws-poc-2026-04-21/load-test-results.csv`
