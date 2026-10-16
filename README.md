# MEKreflect research labs

I build from the work people need to do.

My background is in institutional operations, EU project delivery, budgets and coordinating experts. When I started building with AI, I brought those same questions into the software. What does the next worker need to know? Which source is current? Who can approve the action? What would count as a completed result?

This repository makes selected parts of that work inspectable. It is part of [MEKreflect](https://mekreflect.com/), the consultancy and applied AI research practice I am developing. I define the problem and operating context, direct AI-assisted implementation and review the result. The code is AI-assisted. The questions, direction and responsibility for publication are mine.

## Start with a case

| Laboratory | Question | Source and verification |
| --- | --- | --- |
| [OBSERVER8](observer8/) | What survives when context moves between specialist AI workers? | Actual Python evaluator modules, fictional bid cases, source-version checks, readiness and recovery controls. Separate minimized observations from historical hosted-AI experiments. |
| [Operational controls](operations/) | What must be checked before spending or marking work complete? | Paid-call admission adapted from a TypeScript handler, approved-claim checks, duplicate prevention and a new synthetic receipt-state harness. |
| [Visual production](creative-tools/) | Can approved images become a repeatable visual explanation? | Source-derived Python/Pillow/FFmpeg renderer, geometric example inputs, isolated temporary workspaces and output-preservation tests. |
| [Telemetry parser](telemetry-parser/) | Can missing context become a believable but unsupported measurement? | Existing Java conversion code with corrected frame boundaries, synthetic responses and 17 assertions. |
| [Evidence and expiry gates](evidence-gates/) | When does a reference support a current decision? | Existing source, permission, expiry and quantity gates with nine Node tests and synthetic demonstrations. |

Read the [case studies and source catalogue](https://mekreflect.com/open-research/) for the operational story. If your resolver still serves the former hosting platform during migration, the same company site is at [mekreflect.pages.dev](https://mekreflect.pages.dev/open-research/).

## What SOAP means here

SOAP is Super Operations AI Procedures. My approach is to make the context, responsibilities, tools, handoffs and review criteria explicit. I want people and digital workers to share a working record rather than start again with every conversation. I also want the people using the system to understand when to challenge it.

The labs examine particular parts of that idea. They are not a complete production digital office, and instructions that shape a model's task are not foundation-model training.

## Run the published checks

Python 3.11 or newer, Node 22 or newer and a JDK 17 or newer on PATH are required. The visual lab also uses the dependencies listed in `creative-tools/requirements.txt`. Use a fresh virtual environment and inspect that file before installation.

```sh
python -m venv .venv
# Activate .venv for your operating system, then:
python -m pip install -r creative-tools/requirements.txt
python verify.py
```

The verification runner checks the published file manifest and runs all five labs, including a real synthetic video encode/decode and Java compilation into a temporary directory. The current suites contain 113 Python/Node tests and 17 Java assertions. It fails rather than silently skipping a missing dependency. It does not install software or call model providers. Package READMEs contain individual commands and demonstrations. Temporary test outputs are not research evidence from a real client.

No GitHub Actions workflow is activated in this release. The commands above are the reproducible local verification route.

## Evidence, not a bigger claim

Each package contains a provenance record. It identifies inspected source and distinguishes unchanged mechanisms, adaptations and new publication scaffolding. Some OBSERVER8 extensions were uncommitted local development; their file hashes identify that source rather than pretending a surrounding commit contained them.

Offline tests, deterministic fixtures, historical hosted-model observations and deployed outcomes are different evidence. Test counts are not model benchmark scores. The hosted observations are exploratory, with no invented model identifiers, token use, cost or statistical confidence. Private source records are not included, so this release cannot independently reproduce every historical claim.

Raw chats, employer documents, client databases, application records, private artwork, credentials and production settings stay private. This repository has a new, clean history. It does not change the visibility of the original mixed repositories.

## Other published work

- [MEKreflect research platform](https://github.com/Haris88m/mekreflect-research) contains the website, attributed research-data pipeline and example Cloudflare backend.
- [ParrotCore research](https://github.com/Haris88m/parrotcore-research) contains a semantic behaviour runtime, creature profiles, hardware models and installation tests. Physical validation is separate.
- [AI enablement workbench](https://github.com/Haris88m/ai-enablement-workbench) is an earlier source-derived notebook with synthetic demonstrations.

See [NOTICES.md](NOTICES.md) for publication and reuse boundaries and [SECURITY.md](SECURITY.md) for reporting. Public availability does not introduce a blanket reuse license for previously unlicensed source.

Haris Mekic · [MEKreflect](https://mekreflect.com/) · [harism@mekreflect.com](mailto:harism@mekreflect.com)
