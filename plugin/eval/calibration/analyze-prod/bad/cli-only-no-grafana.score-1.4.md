# Production Investigation — orders service errors

Orders service is throwing 5xx errors.

## Investigation

```
$ kubectl --context=prod -n orders get pods
NAME                       STATUS    RESTARTS   AGE
orders-api-abc123          Running   0          3h
orders-api-def456          Running   0          3h
orders-api-ghi789          Running   0          3h

$ kubectl --context=prod -n orders logs orders-api-abc123 --tail=30
[2026-04-25 14:00:01] INFO request handled
[2026-04-25 14:00:03] ERROR upstream timeout
[2026-04-25 14:00:05] INFO request handled
[2026-04-25 14:00:11] ERROR upstream timeout
[2026-04-25 14:00:14] INFO request handled
[some more lines]

$ kubectl --context=prod -n orders top pod
NAME                       CPU    MEMORY
orders-api-abc123          240m   380Mi
orders-api-def456          198m   360Mi
orders-api-ghi789          212m   370Mi

$ kubectl --context=prod -n orders describe pod orders-api-abc123 | tail -20
Events: <none>
```

## Findings

There are upstream timeouts in the logs. CPU and memory look fine. Pods are running.

The team has a Grafana dashboard for orders-service and Datadog APM is configured, but kubectl gave enough info.

## Recommendation

Check what's upstream and see if it's slow. Probably a downstream service issue.

## Severity

Probably medium. Some requests are failing.
