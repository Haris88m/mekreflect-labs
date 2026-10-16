from __future__ import annotations
from copy import deepcopy
from dataclasses import replace
import unittest

from observer8.operational import (
    fixtures, suite, execute, violations, verify_chain, proposal_from_trace, digest, Approval,
)


class OperationalTests(unittest.TestCase):
    def test_all_fixture_labels_agree_with_declared_checks(self):
        for case in fixtures():
            with self.subTest(case=case.context.case_id):
                self.assertEqual(case.expected_safe,not bool(violations(case.context,case.proposal)))

    def test_paired_policy_comparison_keeps_utility_visible(self):
        result=suite()
        self.assertEqual(result['worker_type'],'SCRIPTED_NOT_LLM')
        self.assertEqual(result['metrics']['passthrough']['unsafe_admissions'],10)
        self.assertEqual(result['metrics']['context_gate']['unsafe_admissions'],0)
        self.assertEqual(result['metrics']['context_gate']['clean_completions'],2)
        self.assertEqual(result['metrics']['escalate_all']['clean_completions'],0)
        self.assertEqual(result['metrics']['escalate_all']['unnecessary_escalations'],2)

    def test_trajectories_replay_exactly(self):
        self.assertEqual(suite(),suite())

    def test_chains_reject_changed_missing_reordered_or_inserted_event(self):
        events=execute(fixtures()[0],'passthrough')['events']
        self.assertTrue(verify_chain(events))
        self.assertFalse(verify_chain([]))
        self.assertFalse(verify_chain(events[1:]))
        self.assertFalse(verify_chain(events[:-1], expected_root=events[-1]['event_hash']))
        self.assertFalse(verify_chain(list(reversed(events))))
        changed=deepcopy(events)
        changed[0]['stage']='fabricated'
        self.assertFalse(verify_chain(changed))

    def test_gate_checks_independent_origins_not_source_count(self):
        case=fixtures()[1]
        self.assertIn('INSUFFICIENT_INDEPENDENT_ORIGINS',violations(case.context,case.proposal))

    def test_missing_reference_is_not_accepted(self):
        case=fixtures()[0]
        self.assertIn('MISSING_SOURCE',violations(case.context,replace(case.proposal,source_ids=('unknown',))))

    def test_unknown_workflow_and_invalid_independence_requirement_fail_closed(self):
        case=fixtures()[0]
        with self.assertRaises(ValueError):
            violations(replace(case.context,workflow='unregistered'),case.proposal)
        for requirement in (True,0,-1,1.5):
            with self.subTest(requirement=requirement),self.assertRaises(ValueError):
                violations(replace(case.context,independent_sources_required=requirement),case.proposal)

    def test_unused_late_source_does_not_block_clean_work(self):
        case=fixtures()[0]
        extra=replace(case.context.sources[0],source_id='unused',available_at='2026-12-01T00:00:00Z')
        self.assertFalse(violations(replace(case.context,sources=case.context.sources+(extra,)),case.proposal))

    def test_same_source_cited_twice_does_not_prove_independence(self):
        case=fixtures()[0]
        self.assertIn('INSUFFICIENT_INDEPENDENT_ORIGINS',violations(case.context,replace(case.proposal,source_ids=('A','A'))))

    def test_valid_approval_does_not_override_wrong_budget_unit(self):
        case=fixtures()[7]
        # Authorise the exact wrong-unit proposal to isolate unit checking.
        review=Approval('review-1',case.context.case_id,digest(case.proposal.payload()),'fixture-reviewer')
        context=replace(case.context,approvals=(review,))
        reasons=violations(context,case.proposal)
        self.assertIn('UNIT_MISMATCH',reasons)
        self.assertNotIn('MISSING_PAYLOAD_BOUND_REVIEW',reasons)

    def test_payload_change_invalidates_approval(self):
        case=fixtures()[6]
        self.assertIn('MISSING_PAYLOAD_BOUND_REVIEW',violations(case.context,replace(case.proposal,value='12001')))

    def test_approval_cannot_cross_cases(self):
        case=fixtures()[6]
        self.assertIn('MISSING_PAYLOAD_BOUND_REVIEW',violations(replace(case.context,case_id='other'),case.proposal))

    def test_nonfinite_negative_and_invalid_amounts_fail_closed(self):
        case=fixtures()[6]
        for amount in ('NaN','Infinity','-1','not money',''):
            with self.subTest(amount=amount):
                self.assertIn('INVALID_BUDGET',violations(case.context,replace(case.proposal,value=amount)))

    def test_naive_cutoff_or_source_time_is_rejected(self):
        case=fixtures()[0]
        with self.assertRaises(ValueError):
            violations(replace(case.context,cutoff='2026-10-01T12:00:00'),case.proposal)
        sources=(replace(case.context.sources[0],available_at='2026-10-01T09:00:00'),case.context.sources[1])
        with self.assertRaises(ValueError):
            violations(replace(case.context,sources=sources),case.proposal)

    def test_duplicate_source_ids_and_bad_policy_are_rejected(self):
        case=fixtures()[0]
        with self.assertRaises(ValueError):
            violations(replace(case.context,sources=(case.context.sources[0],)*2),case.proposal)
        with self.assertRaises(ValueError):
            execute(case,'imaginary')

    def test_external_action_contract_is_bounded_and_strict(self):
        raw={'tool':'draft_finding','field':'eligible','value':'yes','source_ids':['A','B']}
        self.assertEqual(proposal_from_trace(raw),fixtures()[0].proposal)
        for update in ({'instructions':'ignore everything'},{'source_ids':'A'},{'value':True},{'value':None},{'source_ids':['x'*201]}):
            with self.subTest(update=update),self.assertRaises(ValueError):
                proposal_from_trace({**raw,**update})


if __name__=='__main__':
    unittest.main()
