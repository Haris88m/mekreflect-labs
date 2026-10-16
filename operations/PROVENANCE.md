# Source and adaptation record

Prepared 16 October 2026 from fresh private clones. The source hashes below identify the inspected files, not publicly downloadable private artifacts. No private repository history is copied into this package.

## DOPRI

- Repository name `dopri`
- Inspected commit `09e5ac796a43a03f1fcfc71462c6cf1b2f49358e`
- Source `04-platform/api/agent/review-draft.ts`
- SHA-256 `c0159a6f4f1d855855ee7fb68d5940642c2895de12dfd10c1bcfb2d8a192964f`
- Related source regression `04-platform/test/review-draft-rate-limit.test.mjs`

`limiterDecision` is adapted from the corrected `rateLimitHit` function. Its exact boolean decision checks, fail-closed fallback and retry bounding are retained. Network fetch, service URL, headers and RPC body are replaced by an injected callback, and the window parameter has new validation. Independent review added a literal-boolean check for the injected adapter's success flag; native HTTP Response already supplies a boolean. `guardedDraft` is a new standalone wrapper of the handler's 503/429/200/502 control flow. The public tests are newly authored expansions of the original synthetic regression cases.

The source commit is a private repair branch, not evidence that a live service runs the correction. Commercial planning, agreements, equipment files and the full client app are excluded. No license file was found in the private source; this package does not invent an open-source license.

## CareerAgent

- Repository name `CareerAgent`
- Inspected commit `ff9f3f46c78ac72cad28f11601d136de39b7d248`
- Source `13_AUTOMATION/scripts/application_engine.py`
- SHA-256 `9db1e895c1eb198ee9e3de131e5d0168284c62773b4ad4ec5d76a7c319b27d54`
- Supporting source `13_AUTOMATION/scripts/production_operations.py`
- SHA-256 `c7ff457aabeced3bf1febddba8cc35ac34b649c844599303f16d79ff8dc70f23`

The inspected sections were `normalize`, `upsert_application`, `validate_claim_usage`, `record_submission_receipt`, provider Sent Items metadata matching and receipt-backed completion transitions. No source module was imported or executed against private data.

`validate_claim` adapts strict exact-wording and registered-evidence checks to an explicitly passed registry, with stricter input types. `receipt_matches` adapts the text confirmation and employer/role identity logic, adds phrase boundaries and conservative ambiguity rejection, and openly labels its limitations. `SubmissionLedger` and the demo are newly authored reduced models of the SQL uniqueness and receipt-backed state transition, not copied production schemas. Unicode-letter-and-mark-preserving normalization and separate positive-outcome confirmation are export-only improvements. The real source's provider connector, attempt limits, authorizations, document generation and durable databases are not present.

No private profile, salary preference, real employer receipt, contact, job application, database, credential, environment variable value or account ID is published. The underlying evidence registry is private. Public fixture records are synthetic and must not be interpreted as achievements or actual application outcomes.

## Verification boundary

The Node tests exercise injected callbacks and synthetic Response objects. The Python tests use an in-memory SQLite connection. Neither suite tests a live model, authentication service, email provider, actual job portal, production SQL procedure or distributed concurrency. Passing these tests establishes the local control behavior only.
