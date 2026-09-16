# AI Usage

## Tools used

- Claude (Anthropic): coaching and guidance throughout
- GitHub Copilot: line-level completion

## Tasks

- Breaking assessment into phases, understanding scoring weights
- Explaining FastAPI idempotency via Response object
- Debugging SQLite BIGINT PK autoincrement issue
- Explaining Kubernetes readiness vs liveness probes
- Debugging base64 truncation in Kubernetes Secrets

## Representative prompts

1. Idempotent payment returns 201 on replay instead of 200.
   Decorator says status_code=201. How do I override for the replay case?

2. kubectl get endpoints shows none but pods are Running.
   What commands tell me if this is a selector problem or port problem?

3. EXPLAIN shows Seq Scan reading 49999 rows.
   What index fixes this and what does ANALYZE do after?

4. My 401 test fails with KeyError on response.json()['error'].
   What shape does FastAPI return for HTTPException vs custom handler?

5. Kubernetes Secret says unchanged but wrong value is stored.
   Why does kubectl apply not update a Secret value?

## Validation method

- Ran every code suggestion before accepting it
- Verified SQL queries against real 50k dataset, cross-checked counts
- Applied Kubernetes manifests to real cluster, watched pods come up
- Checked EXPLAIN plans before and after index change
- Reproduced every incident manually with real terminal output

## Where I corrected AI output

Response status override: Claude suggested JSONResponse for idempotent 200.
That broke response_model validation. Correct fix is injecting FastAPI
Response object and setting response.status_code = 200.

base64 line wrapping: Claude said echo -n ... | base64 which wraps at
76 chars and corrupts Kubernetes Secrets. Fix: base64 -w 0.
Discovered by decoding the stored secret and seeing truncated URL.

SQLite BIGINT: Generated models used BigInteger for PKs which breaks
SQLite autoincrement. Fixed with BigInteger().with_variant(Integer, sqlite).
