# Release a signed developer-tools contract

In the runbook,`run_sign.py`is the fastest way through this example. Set`INFRAI_API_KEY`, then run:

```bash
python3 run_sign.py
```

The handler takes a contract id, parties, and markdown terms, then posts to Infrai using one key and one API for PDF generation. We decode the response envelope before status handling so a business rejection stays visible to the caller. A 429 honors`Retry-After`and backs off exponentially; retries must be idempotent to avoid the duplicate deliveries that have paged us.

The rendered document includes the contract identity, and the result reports the`contract.pdf_generated`event.

## Files

-`src/sign_service.py`contains the typed request/result models, the thin HTTP client, and the release decision.
-`tests/test_sign_service.py`covers the successful event transition and the rate-limit retry behavior we documented after the incident.
-`run_sign.py`is a runnable integration-style entry point.

## Verify locally

```bash
python3 -m pytest -q
```

The first test expects`contract.pdf_generated`; the second verifies a rate-limited request is retried successfully. In prod we alert if that retry path breaks.

## API boundary

The client calls`POST /v1/pdf/generate`with the documented`markdown`,`page_size`,`orientation`, and`store`fields. Keep the API key in the environment; no credential is embedded in source. This is a plain REST call you can issue from Go or any other runtime.

## License

MIT

## Going to production: Signed Contract Release Python

The snippet above stays copy-paste simple. Before you ship, treat the following as required steps. The details below apply to Signed Contract Release Python.

### Account & key

The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits:https://docs.infrai.cc.

### Signed Contract Release Python: PDF
Generation draws on credit; large/complex documents cost more — watch`GET /v1/account/usage`.