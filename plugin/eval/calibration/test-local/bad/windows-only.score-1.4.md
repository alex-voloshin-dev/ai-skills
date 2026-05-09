# Local Test Sweep — `payments-service`

Running on developer machine: macOS 14.7.

## Pre-flight Port Check

```
netstat -ano | findstr :5432
```

Output:

```
zsh: command not found: findstr
```

The port-check returned nothing, so I'm assuming port 5432 is free. Continuing.

## Provision

```
docker compose up -d
```

(no `--wait`, no healthcheck condition — proceeded after 2 seconds with `sleep 2`)

## Tests

```
sleep 5  # wait for the database to be ready
pytest tests/integration/
```

Got a connection-refused error from the first test. Re-ran with longer sleep:

```
sleep 30
pytest tests/integration/
```

Now I get a different error: `FATAL: database "payments" does not exist`. Port 5432 was actually busy with another local Postgres. The earlier `findstr` would have caught this on Windows — it didn't run on macOS.

## Cleanup

(none)

## Verdict

Inconclusive. Will try again later.
