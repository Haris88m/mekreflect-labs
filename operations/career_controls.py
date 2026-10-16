"""CareerAgent-derived research controls. Offline only; this never applies for jobs.

Original private schemas and records are deliberately not exported. The small
SQLite harness makes duplicate and receipt transitions inspectable in isolation.
"""
from __future__ import annotations

import hashlib
import re
import sqlite3
import unicodedata


def normalize(value: str) -> str:
    """Retain letters from all scripts; punctuation and whitespace are separators."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Identity fields must be nonempty strings")
    text = unicodedata.normalize("NFKC", value).casefold()
    result = " ".join("".join(c if c.isalnum() or unicodedata.category(c).startswith("M") else " " for c in text).split())
    if not result or not any(c.isalnum() for c in result):
        raise ValueError("Identity fields must contain letters or numbers")
    return result


def validate_claim(entry: dict, approved: dict) -> None:
    """Strict exact-wording gate adapted from validate_claim_usage.

    The registry is an explicit dependency instead of a private profile file.
    This verifies a declaration against a registry, not the truth of the registry.
    """
    if not isinstance(entry, dict) or not isinstance(approved, dict):
        raise ValueError("Claim and approval must be objects")
    if approved.get("application_safe") is not True:
        raise ValueError("Claim is not approved")
    if not isinstance(entry.get("claim_id"), str) or not entry["claim_id"] or entry["claim_id"] != approved.get("claim_id"):
        raise ValueError("Claim identity does not match")
    evidence = entry.get("evidence_ids")
    registered = approved.get("evidence_ids")
    if (not isinstance(evidence, list) or not evidence
            or not isinstance(registered, list)
            or any(not isinstance(item, str) or not item for item in evidence + registered)
            or not set(evidence).issubset(set(registered))):
        raise ValueError("Evidence references are missing or unapproved")
    wording = entry.get("exact_wording")
    variants = approved.get("allowed_wording")
    if (not isinstance(wording, str) or not wording.strip()
            or not isinstance(variants, list)
            or any(not isinstance(item, str) for item in variants)
            or " ".join(wording.casefold().split()) not in {
                " ".join(item.casefold().split()) for item in variants
            }):
        raise ValueError("Wording is not an exact approved variant")


def receipt_matches(text: str, employer: str, role: str, application_id: str) -> bool:
    """Text consistency heuristic, NOT receipt authenticity verification.

    A trusted connector and human review must establish provenance separately.
    No screenshot/PDF parsing or employer contact is performed here.
    """
    if not isinstance(text, str) or not text.strip():
        return False
    folded = text.casefold()
    # Conservative rejection only, not a general natural-language classifier.
    # Ambiguity must remain for review even when the source itself is authentic.
    if re.search(r"\b(no|not|never|if|unless|until|after|before|would|could|might|sample|template|failed|unsuccessful|pending)\b|n['’]t\b|\bexample\s+(message|status|receipt)\b", folded):
        return False
    normalized = normalize(text)
    confirmation_terms = (
        "application submitted", "successfully submitted", "application received",
        "thank you for applying", "submission confirmation", "application confirmation",
    )
    def phrase_present(phrase: str) -> bool:
        return f" {normalize(phrase)} " in f" {normalized} "
    identity_matches = phrase_present(role) or bool(
        application_id and re.search(r"(?<![\w-])" + re.escape(application_id.casefold()) + r"(?![\w-])", folded)
    )
    return any(term in folded for term in confirmation_terms) and phrase_present(employer) and identity_matches


class SubmissionLedger:
    """New research harness derived from CareerAgent's SQL uniqueness and state gates."""
    def __init__(self):
        self.db = sqlite3.connect(":memory:")
        self.db.execute("""CREATE TABLE applications (
            id TEXT PRIMARY KEY, employer TEXT NOT NULL, role TEXT NOT NULL,
            location TEXT NOT NULL, state TEXT NOT NULL DEFAULT 'Prepared',
            receipt_sha256 TEXT,
            UNIQUE(employer, role, location)
        )""")

    def close(self):
        self.db.close()

    def prepare(self, employer: str, role: str, location: str) -> tuple[str, bool]:
        identity = tuple(normalize(value) for value in (employer, role, location))
        existing = self.db.execute("SELECT id FROM applications WHERE employer=? AND role=? AND location=?", identity).fetchone()
        if existing:
            return existing[0], False
        key = "APP-" + hashlib.sha256("|".join(identity).encode()).hexdigest()[:24]
        self.db.execute("INSERT INTO applications(id,employer,role,location) VALUES(?,?,?,?)", (key, *identity))
        self.db.commit()
        return key, True

    def mark_submitted(self, key: str, receipt: str, *, provenance_confirmed: bool, outcome_confirmed: bool = False) -> None:
        row = self.db.execute("SELECT employer,role,state FROM applications WHERE id=?", (key,)).fetchone()
        if not row or row[2] != "Prepared":
            raise ValueError("Unknown or already submitted application")
        if provenance_confirmed is not True:
            raise ValueError("Receipt provenance requires separate confirmation")
        if outcome_confirmed is not True:
            raise ValueError("Positive submission outcome requires separate confirmation")
        if not receipt_matches(receipt, row[0], row[1], key):
            raise ValueError("Receipt does not establish confirmation and identity")
        digest = hashlib.sha256(receipt.encode()).hexdigest()
        self.db.execute("UPDATE applications SET state='Submitted',receipt_sha256=? WHERE id=?", (digest, key))
        self.db.commit()

    def status(self, key: str):
        return self.db.execute("SELECT state,receipt_sha256 FROM applications WHERE id=?", (key,)).fetchone()
