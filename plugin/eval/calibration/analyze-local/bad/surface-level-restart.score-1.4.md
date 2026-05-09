# Local Container Issue

The `api` container is having problems.

## What I Saw

```
$ docker ps
CONTAINER     STATUS
api           Restarting
postgres      Up
worker        Up
```

The api container is restarting.

## Recommendation

Just restart the container:

```
docker compose restart api
```

If that doesn't work, restart the whole stack:

```
docker compose down
docker compose up -d
```

If still broken, run `docker system prune -af --volumes` to clean everything up and start fresh.

## Notes

- Restarts usually fix this
- The whole stack restart is a good fallback
- Full prune wipes all state but is the most reliable
