from __future__ import annotations
from copy import deepcopy
import unittest
from observer8.bid_readiness import cases,normalise_manager,payload_for,specialist_packet

def proposal(case):
    return {'case_id':case['context']['case_id'],**case['facts'],'readiness':'READY_TO_SUBMIT',
            'approval_id':case['trusted_test_approval']['approval_id'] if case['trusted_test_approval'] else None}

class ReadyTests(unittest.TestCase):
    def test_qualified_approved_case_reaches_mock_sink(self):
        case=cases()[0];result=normalise_manager(proposal(case),case)
        self.assertEqual(result['controller_route'],'MOCK_SUBMISSION_RECORDED')
        self.assertEqual(result['guard_findings'],[])
        self.assertFalse(result['external_submission'])
        self.assertEqual(result['mock_record']['payload'],payload_for(case['context']['case_id']))

    def test_holding_a_ready_case_is_not_counted_as_success(self):
        case=cases()[0];raw=proposal(case);raw['readiness']='HOLD'
        self.assertEqual(normalise_manager(raw,case)['controller_route'],'HOLD')

    def test_approval_missing_blocks_even_if_model_claims_ready(self):
        case=cases()[1];raw=proposal(case);raw['approval_id']='model-says-approved'
        self.assertIn('NO_VALID_PAYLOAD_BOUND_TEST_APPROVAL',normalise_manager(raw,case)['guard_findings'])

    def test_reference_and_capacity_gaps_survive_model_confidence(self):
        case=cases()[2];result=normalise_manager(proposal(case),case)
        self.assertIn('REFERENCE_GAP',result['guard_findings'])
        self.assertIn('CAPACITY_GAP',result['guard_findings'])

    def test_changed_payload_case_or_context_invalidates_approval(self):
        for field,value in [('budget_total_eur',126001),('case_id','other'),('contract_cap_eur',180000)]:
            case=cases()[0];raw=proposal(case);raw[field]=value
            with self.subTest(field=field):self.assertEqual(normalise_manager(raw,case)['controller_route'],'HOLD')
        case=cases()[0];case['context']['sources'][0]['text']='changed'
        self.assertIn('CONTEXT_CHANGED_AFTER_TEST_APPROVAL',normalise_manager(proposal(case),case)['guard_findings'])

    def test_string_booleans_and_wrong_mode_do_not_prove_approval(self):
        for field,value in [('verified_by_test_registry','true'),('mode','PRODUCTION')]:
            case=cases()[0];case['trusted_test_approval'][field]=value
            with self.subTest(field=field):self.assertFalse(normalise_manager(proposal(case),case)['synthetic_approval_valid'])

    def test_boolean_is_not_integer_money(self):
        case=cases()[0];raw=proposal(case);raw['budget_total_eur']=True
        self.assertIn('INVALID_TYPE:budget_total_eur',normalise_manager(raw,case)['guard_findings'])

    def test_prompt_excludes_evaluation_outcomes(self):
        for role in ('business_development','bid_management','data_compliance'):
            packet=specialist_packet(role)
            self.assertNotIn('expected_route',str(packet))
            self.assertNotIn('display_label',str(packet))

if __name__=='__main__':unittest.main()
