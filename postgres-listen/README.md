# Usage

Listen to a postgres channel and send the webhook to a url.

```
PGUSER=postgres PGPASSWORD=changeme PGDATABASE=windmill CHANNEL=mychannel WEBHOOK=https://app.windmill.dev/api/w/github-sync-example/jobs/run/p/f/examples/query_postgres?token=secret deno run -A postgres-listen/main.ts
```

To test, run the following in psql:

```
notify mychannel, '{"foo": 42}
```
