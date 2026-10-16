import copy
import hashlib
import unittest
from career_controls import SubmissionLedger, normalize, receipt_matches, validate_claim


class CareerControlTests(unittest.TestCase):
    def setUp(self):
        self.ledger = SubmissionLedger()
        self.approved = {
            "claim_id": "SYNTHETIC-1", "application_safe": True,
            "evidence_ids": ["DEMO-EVIDENCE-1"],
            "allowed_wording": ["Coordinated two synthetic project workstreams."],
        }
        self.claim = {
            "claim_id": "SYNTHETIC-1", "evidence_ids": ["DEMO-EVIDENCE-1"],
            "exact_wording": "Coordinated two synthetic project workstreams.",
        }

    def tearDown(self):
        self.ledger.close()

    def test_normalized_duplicates_return_same_record(self):
        first = self.ledger.prepare("Example Labs", "Project Manager", "Remote")
        second = self.ledger.prepare("EXAMPLE-LABS", "  Project   Manager ", "remote")
        self.assertTrue(first[1])
        self.assertEqual(second, (first[0], False))

    def test_different_location_is_separate(self):
        a = self.ledger.prepare("Example", "Manager", "Remote")
        b = self.ledger.prepare("Example", "Manager", "London")
        self.assertNotEqual(a[0], b[0])

    def test_unicode_names_do_not_collapse_to_empty(self):
        self.assertEqual(normalize("  ПРИМЕР "), "пример")
        self.assertNotEqual(normalize("Пример"), normalize("Друг"))

    def test_combining_marks_distinguish_identity(self):
        self.assertNotEqual(normalize("की"), normalize("क"))
        self.assertNotEqual(normalize("कि"), normalize("क"))
        self.assertNotEqual(normalize("কি"), normalize("ক"))
        self.assertEqual(normalize("Cafe\u0301"), normalize("Café"))

    def test_blank_identity_rejected(self):
        for value in ("", " ", "---", None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                normalize(value)

    def test_approved_claim_passes(self):
        validate_claim(self.claim, self.approved)

    def test_claim_whitespace_and_case_do_not_change_meaning(self):
        self.claim["exact_wording"] = " COORDINATED  two synthetic project workstreams. "
        validate_claim(self.claim, self.approved)

    def test_unapproved_strengthening_rejected(self):
        self.claim["exact_wording"] = "Managed twenty paying customers."
        with self.assertRaises(ValueError):
            validate_claim(self.claim, self.approved)

    def test_unapproved_evidence_rejected(self):
        self.claim["evidence_ids"] = ["NOT-REGISTERED"]
        with self.assertRaises(ValueError):
            validate_claim(self.claim, self.approved)

    def test_string_not_accepted_as_evidence_list(self):
        self.claim["evidence_ids"] = "DEMO-EVIDENCE-1"
        with self.assertRaises(ValueError):
            validate_claim(self.claim, self.approved)

    def test_truthy_approval_does_not_pass(self):
        for value in ("true", 1, [], None, False):
            with self.subTest(value=value), self.assertRaises(ValueError):
                record = copy.deepcopy(self.approved)
                record["application_safe"] = value
                validate_claim(self.claim, record)

    def test_wrong_claim_identity_rejected(self):
        self.claim["claim_id"] = "OTHER"
        with self.assertRaises(ValueError):
            validate_claim(self.claim, self.approved)

    def test_receipt_requires_employer_and_role(self):
        self.assertFalse(receipt_matches("Application received at Other Labs for Project Manager", "Example Labs", "Project Manager", "APP-DEMO"))
        self.assertFalse(receipt_matches("Application received at Example Labs for Designer", "Example Labs", "Project Manager", "APP-DEMO"))

    def test_employer_substring_is_not_identity(self):
        self.assertFalse(receipt_matches("Application received at Counterexample Labs for Manager", "Example Labs", "Manager", "APP-DEMO"))

    def test_application_id_substring_is_not_identity(self):
        self.assertFalse(receipt_matches("Application received at Example Labs for APP-DEMO-extra", "Example Labs", "Manager", "APP-DEMO"))

    def test_receipt_application_id_can_identify_role(self):
        self.assertTrue(receipt_matches("Application received at Example Labs APP-DEMO", "Example Labs", "Manager", "APP-DEMO"))

    def test_receipt_requires_confirmation_language(self):
        self.assertFalse(receipt_matches("Example Labs Project Manager is open", "Example Labs", "Project Manager", "APP-DEMO"))

    def test_negative_and_conditional_receipts_do_not_confirm(self):
        for text in (
            "Application not successfully submitted to Example Labs for Project Manager",
            "No application received by Example Labs for Project Manager",
            "If application received by Example Labs for Project Manager, we will email you",
            "Application received by Example Labs for Project Manager would appear here after submission",
            "Application received by Example Labs for Project Manager is a sample status message",
            "After your application submitted at Example Labs for Project Manager we will contact you",
        ):
            with self.subTest(text=text):
                self.assertFalse(receipt_matches(text, "Example Labs", "Project Manager", "APP-DEMO"))

    def test_prepared_does_not_mean_submitted(self):
        key, _ = self.ledger.prepare("Example Labs", "Project Manager", "Remote")
        self.assertEqual(self.ledger.status(key), ("Prepared", None))

    def test_content_alone_does_not_establish_provenance(self):
        key, _ = self.ledger.prepare("Example Labs", "Project Manager", "Remote")
        with self.assertRaises(ValueError):
            self.ledger.mark_submitted(key, "Application received at Example Labs for Project Manager", provenance_confirmed=False)
        self.assertEqual(self.ledger.status(key), ("Prepared", None))

    def test_authentic_message_does_not_prove_positive_outcome(self):
        key, _ = self.ledger.prepare("Example Labs", "Project Manager", "Remote")
        with self.assertRaises(ValueError):
            self.ledger.mark_submitted(key, "Application received at Example Labs for Project Manager", provenance_confirmed=True)
        self.assertEqual(self.ledger.status(key), ("Prepared", None))

    def test_wrong_receipt_leaves_state_prepared(self):
        key, _ = self.ledger.prepare("Example Labs", "Project Manager", "Remote")
        with self.assertRaises(ValueError):
            self.ledger.mark_submitted(key, "Application received at Other Labs", provenance_confirmed=True, outcome_confirmed=True)
        self.assertEqual(self.ledger.status(key), ("Prepared", None))

    def test_confirmation_records_exact_content_digest(self):
        key, _ = self.ledger.prepare("Example Labs", "Project Manager", "Remote")
        text = "Application received at Example Labs for Project Manager"
        self.ledger.mark_submitted(key, text, provenance_confirmed=True, outcome_confirmed=True)
        self.assertEqual(self.ledger.status(key), ("Submitted", hashlib.sha256(text.encode()).hexdigest()))
        with self.assertRaises(ValueError):
            self.ledger.mark_submitted(key, text, provenance_confirmed=True, outcome_confirmed=True)

    def test_unknown_application_cannot_be_submitted(self):
        with self.assertRaises(ValueError):
            self.ledger.mark_submitted("NOT-REGISTERED", "Application received", provenance_confirmed=True)


if __name__ == "__main__":
    unittest.main()
