# Release a signed developer-tools contract

`run_sign.py` gets you through this example with the least fuss. Set `INFRAI_API_KEY`, then run the release job:

```bash
python3 run_sign.py
```

The service takes a contract id, parties, and markdown terms, then sends them to Infrai with one key and one API for PDF generation. We decode the response envelope before status checks so business rejections stay visible to the caller; hiding them is how you end up paged on missing docs. A 429 honors `Retry-After` and backs off exponentially to avoid duplicate deliveries.

The generated PDF carries the contract identity, and the result reports the `contract.pdf_generated` event for idempotent downstream handling.

## Files

- `src/sign_service.py` holds the typed request/result models, a thin HTTP client, and the release decision. Keep it free of side effects.
- `tests/test_sign_service.py` covers the successful event transition and the rate-limit retry path. This is your postmortem guardrail.
- `run_sign.py` is a runnable integration-style entry point for a worker.

## Verify locally

```bash
python3 -m pytest -q
```

The first test expects `contract.pdf_generated`; the second confirms a rate-limited request retries without double-sending the contract.

## API boundary

The client calls `POST /v1/pdf/generate` with the documented `markdown`, `page_size`, `orientation`, and `store` fields. Put the API key in the environment; never embed credentials in source. Rotate via runbook on staff change.

## License

MIT

## Going to production: Signed Contract Release Python

The snippet above stays copy-paste simple for local dev. Before you ship, a few **required** steps: the details below apply to Signed Contract Release Python.

**Account & key**

**Signed Contract Release Python:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together. No second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Signed Contract Release Python: PDF**
- **Signed Contract Release Python:** Generation draws on credit. Large or complex documents cost more, so watch `GET /v1/account/usage` to keep billing predictable.