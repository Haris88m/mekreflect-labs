"""Synthetic offline walkthrough; no application or email is sent."""
import json
from career_controls import SubmissionLedger

ledger = SubmissionLedger()
key, created = ledger.prepare("Example Research", "Programme Manager", "Remote")
print(json.dumps({"stage": "prepared", "created": created, "status": ledger.status(key)}))
_, duplicate_created = ledger.prepare("EXAMPLE RESEARCH", "Programme Manager", "remote")
print(json.dumps({"stage": "duplicate_check", "new_record_created": duplicate_created}))
try:
    ledger.mark_submitted(key, "A draft is ready", provenance_confirmed=True, outcome_confirmed=True)
except ValueError as error:
    print(json.dumps({"stage": "invalid_receipt_blocked", "reason": str(error), "status": ledger.status(key)}))
ledger.mark_submitted(key, "Application received by Example Research for Programme Manager", provenance_confirmed=True, outcome_confirmed=True)
print(json.dumps({"stage": "synthetic_confirmation", "status": ledger.status(key)}))
ledger.close()
