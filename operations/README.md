# Operational controls from my AI development

Part of [MEKreflect](https://mekreflect.com), my applied research into how people and AI systems carry work forward together.

I wanted AI to do useful work without losing the controls I rely on in operations. A draft is not a completed action. A plausible claim is not evidence. A failed cost-control service is not permission to keep spending. These two case studies expose small, testable parts of the systems I developed with AI coding agents.

## Case study 1. A paid draft needs permission to run

DOPRI includes a review-response drafting feature for local businesses. Its private implementation checks a feature flag, authenticates a user, looks for their profile, asks a rate limiter for permission and then requests a model-generated draft. The model's response is a draft, not an automatically published reply.

A focused review found that an unavailable or malformed limiter response could let a paid call proceed. The private correction requires an explicit boolean allow decision. Seven failure shapes now stop before generation. A valid denial returns a retry interval, and a valid allow permits one generation attempt. The same private regression suite failed eight cases against the original handler and passed all ten against the patch. That correction is in a private, unmerged pull request, not a production deployment claim.

`paid-call-control.mjs` extracts the admission decision and execution boundary into an offline lab. The actual service URL, authentication, database and provider request are replaced by injected callbacks. Its tests count generation calls rather than trusting a success message. They also cover retry bounds and redacted generation errors. No API key, model subscription, Supabase project or network access is needed.

This does not implement a distributed rate limiter or a hard currency budget. The production RPC still needs concurrency, authorization and database verification. A timeout adapter must enforce its own deadline. The test suite simulates failures and model results; it does not measure model quality.

## Case study 2. An application has to survive its own evidence checks

CareerAgent grew out of my own job search. I directed AI agents to research roles, organize evidence, prepare company-specific material and preserve a clear distinction between preparation, authorization, sending and confirmation. The private implementation includes SQLite records, duplicate detection, claim wording checks, attempt tracking and receipt reconciliation.

I am publishing the control pattern, not my CV archive or another person's correspondence. `career_controls.py` makes three parts inspectable.

1. A normalized employer, role and location identify a record. Repeated preparation returns the existing record.
2. Strict claims must use registered evidence IDs and an exact approved wording variant. The checker cannot establish whether the underlying evidence is true; that is a separate human review.
3. A record becomes submitted only after confirmation text matches its identity and both provenance and positive-outcome confirmations are supplied separately. The exact receipt text is hashed. A hash detects later changes; it does not authenticate the sender or establish success.

The exported SQLite ledger is a newly written, in-memory research harness based on the private application's state and uniqueness gates. It is not the original database or a complete submission engine. No browser, account, live mail or external submission capability is included. The text-matching function is a heuristic, not a fraud detector. It rejects common negative and conditional words conservatively, which can also reject a legitimate receipt with unrelated qualifying language. It cannot interpret every sentence. Positive outcome must therefore be explicitly confirmed separately from source authenticity. These injected booleans represent upstream decisions, not authenticated review tokens or production authorization.

During extraction and independent review I tightened the public boundaries. Approval and adapter success must be literal booleans. Identity normalization retains Unicode letters and combining marks instead of collapsing distinct names. Common negative or conditional receipts cannot imply completion, and positive outcome is a separate review decision. These improvements are not silently claimed to have been deployed in the original private system.

## Run it

Use Node 22 or newer and Python 3.10 or newer. No third-party dependencies are required.

```sh
node --test paid-call-control.test.mjs
python -m unittest -v test_career_controls.py
python demo.py
```

All fixture organizations, evidence IDs, replies and receipts are invented. The demo prints a preparation, a prevented duplicate, a rejected receipt and a synthetic confirmed state. It never sends an application.

## What this demonstrates

My contribution is the operational framing, context, acceptance criteria and review of the result. The implementation is AI-assisted. These examples connect human expectations to explicit code boundaries and regression tests. They are small enough for another engineer to inspect, reproduce and challenge.

Source provenance and the exact publication boundary are in [PROVENANCE.md](PROVENANCE.md). No original private history, account configuration, employer archive, client database, real receipt or personal contact list is included. Original source remains private. No blanket software reuse license is newly granted by this extraction.
