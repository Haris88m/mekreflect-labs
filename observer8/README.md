# OBSERVER8 Handoff Lab

## Can the next AI worker still tell what is known?

I build workflows around the work people actually need to finish. In bidding, the useful answer is not simply a persuasive proposal. Someone must know which tender version governs, whether the experts are available, how the budget was calculated and who can approve the submission.

That became the question behind this part of OBSERVER8. I wanted to see what happens when specialist AI workers pass an operational decision between them. Does the deadline remain current? Does an old summary become an accepted fact? Can a cautious system still let complete, approved work proceed?

This is the inspectable Python core of that experiment. It sits within my [MEKreflect research and development](https://mekreflect.com/) and SOAP approach, Super Operations AI Procedures. I define the operational problem and contextual SOPs, direct AI-assisted implementation and review the resulting behaviour. This release contains actual evaluator mechanisms and fictional development cases, not client files or a live bidding service.

## Start here

Python 3.11 or newer. No third-party dependencies, credentials, model subscription or network connection is needed.

From this folder:

```sh
python -m unittest discover -s tests -v
python -m observer8 controls
python -m observer8 demo
python -m observer8 packet O8-BID-202
```

`controls` runs twelve scripted fixtures under three policies. `demo` shows six more complex synthetic cases with an authored oracle response so the controller and retrieval behaviour can be inspected. **Neither command runs an AI model.** The exported packet is a genuine source context for a future model experiment, but obtaining a response is the caller's separate action.

To inspect a JSON response you obtained yourself, either the contract's single-case `{"cases":[...]}` envelope or a direct case object:

```sh
python -m observer8 evaluate O8-BID-202 response.json
python -m observer8 evaluate O8-BID-202 response.json --phase requested-recovery
```

The second command retrieves only source IDs requested in that response. It does not ask a model to reason again, rewrite the answer or send a bid. A true recovery experiment must give the returned records to a fresh reasoning step and separately retain that step's input and output. Responses are untrusted data, never executable instructions.

## The workflow I designed

```text
Versioned tender and operational evidence
             |
    Business development    Bid management    Data and compliance
             |                    |                    |
             +--------- Operational synthesis --------+
                                  |
                         Receiving bid manager
                                  |
                 Source, fact and test-authority checks
                         /                  \
                 Hold with reasons     Local mock receipt
```

The role instructions in `observer8/bid_case.py` distinguish company eligibility, preparation planning and compliance/budget review. Shared context is not just a long prompt. It is a source register with document roles, precedence, timestamps, evidence status and field dependencies. The source of a deadline is different from the source of an expert's confirmed availability.

The workflow topology grew out of my opportunity and bid-management work in the Salience context. This publication makes no claim of company endorsement, paid commissioning or operational adoption. Every tender, reference, expert, price and approval in the released fixtures is fictional.

## What the code does

| Mechanism | Implementation | What it makes inspectable |
| --- | --- | --- |
| Source-dependent fields | `observer8/bid_handoff.py` | Missing evidence clears the affected current field while retaining its received value separately. It does not erase unrelated supported fields. |
| Budget and evidence controls | `observer8/operational.py` | Currency, units, spending limits, source independence, cutoff dates and bounded proposed actions. |
| Payload-bound test approval | `observer8/bid_readiness.py` | A changed case, context or proposed payload cannot reuse a synthetic approval. |
| Bounded retrieval | `observer8/bid_complex.py` | Only requested source IDs return from the local synthetic store. Unknown IDs do not invent documents. |
| Utility-aware review | `observer8/bid_complex.py` | A hold on a ready-labelled case is visible and must be examined rather than automatically praised as safety. |
| Replay consistency | `observer8/operational.py`, `strict_json.py` | Deterministic traces, retained-root hash checking and finite JSON. Hashes are not signatures or proof against a writer who replaces both trace and root. |

The code deliberately keeps authority outside the model's prose. A recommendation that says “approved” is not an authenticated approval. The public source-manifest guard never grants an external action. More advanced case controllers can create only a local mock record.

## Six complex cases

| Case | Complication | Question |
| --- | --- | --- |
| 201 | Complete current records plus stale commentary | Can genuinely complete work proceed despite non-authoritative caution? |
| 202 | Missing second addendum | Can the worker request the governing source instead of promoting an old deadline? |
| 203 | GBP fees, EUR expenses and a missing planning rate | Does the budget retain its units and conversion assumptions across roles? |
| 204 | Withdrawn reference and reduced lead capacity | Does retrieval expose the blocker rather than silently repair eligibility? |
| 205 | Revised price after approval | Does the approval still cover the exact proposed amount? |
| 206 | Two official notices with different lot scope | Can source authority and scope resolve a conflict that timestamps alone cannot? |

The controller's oracle demonstration yields four mock receipts and two holds after requested retrieval. That is a control result under authored facts, **not the observed behaviour of the hosted AI workers**. The historical AI run held more cases, as described below.

## What I learned from actual AI runs

The separately recorded experiments involved 23 hosted AI tasks across ten fictional cases. The first pilot used six tasks for one case. The readiness pilot used seven tasks for three cases. The complex pilot used eight initial/recovery tasks and two additional interface-diagnostic tasks over a six-case batch. These counts are not independent statistical trials.

The first lossy-context worker recognised missing information in prose but still returned a superseded deadline and contract cap in fields named `current_deadline` and `contract_cap_eur`. The source-bound worker returned the amended values. The input loss was deliberately introduced by the evaluator, not observed spontaneous model memory loss. No bid was submitted. This motivated field-level source dependencies instead of relying on a prose caveat that software might ignore.

The readiness pilot allowed its complete, test-approved case through to a mock receipt while holding missing approval and actual eligibility gaps. In the complex pilot, requested documents were successfully forwarded and recovery resolved the unknown scalar fields. However, three ready-labelled cases remained held because workers disputed finished-package reconciliation and existing approval applicability. Clarifying exact hash preimages did not change those outcomes in this small exploratory comparison.

That disagreement is part of the result. A source/payload hash does not prove the final proposal documents were reconciled after an amendment. The authored readiness labels use a scalar-payload interpretation; the workers raised a package-level objection. I cannot fairly turn these holds into either a universal safety success or a proven unnecessary-blocking failure.

The minimized historical observations are in [`data/recorded-observations.json`](data/recorded-observations.json). They are transcribed from saved local run reports, not provider-signed responses. Raw prompts, transcripts, task identifiers and private capture records are intentionally not in this release. Therefore this export reproduces controller behaviour, not an independent replay of the historical hosted runs. Exact model IDs, token use, latency and marginal costs were not available and are not invented.

## Verification and boundaries

This public extraction has **46 passing offline tests**, including source loss, readiness, retrieval, budget units, changed approvals, malformed values, replay and CLI checks. The twelve scripted controls comprise ten unsafe-labelled and two clean fixtures. Passthrough admits all ten unsafe cases, the configured gate blocks those ten while completing the two clean cases, and blanket escalation blocks both useful cases. The expected labels and checks were authored together; this is implementation verification, not independent model validation.

The operational controllers know authored fixture facts. They do not solve arbitrary document truth, authenticate humans, certify prompt-injection resistance or implement production IAM. The historical worker tool restrictions were instructions, not a hardened sandbox. No client adoption, measured staff time savings, paid API run, live submission or general model-safety claim follows from these tests.

My next research step is independently authored cases and explicit package-level completion evidence, followed by a frozen holdout and controlled repeated model runs. I want to measure useful completion, source loss, correction effort and genuinely unnecessary escalation together. A system that refuses everything has not learned to run an office.

## Provenance

[`PROVENANCE.json`](PROVENANCE.json) identifies the local source snapshot and SHA-256 hashes. The original operational extension was uncommitted when exported; the base repository commit is context, not a false claim that it contained these new files. Six core Python modules are unchanged. The seventh adds enforcement of its existing five-finding output limit. Two original test files are unchanged. One original complex-case test was adapted to the public input exporter. The offline CLI and twelve public-boundary tests were added for this release. Independent review caught a response-envelope mismatch in that new CLI; the corrected command accepts the actual output contract and rejects duplicate or wrong case IDs.

The broader private Simulation repository is a distinct possibility-engine project. Its source, credentials, deployments and large histories are not bundled here. This focused release makes the operational-handoff work understandable on its own. Public availability does not add a blanket reuse license or grant rights over third-party material.
