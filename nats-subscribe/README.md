# Usage

Listen on a NATS PubSub subject and send the webhook to a URL.

```
NATS_URL=nats://localhost:4222 SUBJECT=mysubject WEBHOOK=https://app.windmill.dev/api/w/github-sync-example/jobs/run/p/f/examples/query_postgres python3 nats-subscribe/main.py
```

To test, run the following in a shell:

```
NATS_URL=nats://localhost:4222 nats publish mysubject '{"foo": 42}'
```

Note that the subject of the received message will be included in an
`X-NATS-Subject` header. This can be useful in combination with Windmill's
[request headers](https://www.windmill.dev/docs/core_concepts/webhooks#request-headers)
functionality.
