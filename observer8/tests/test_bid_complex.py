from copy import deepcopy
import unittest
from observer8.bid_complex import fixtures,recover,inspect,validate,context_hash
from observer8.operational import digest
from observer8.__main__ import model_packet

def proposal(case,ready='READY_TO_SUBMIT'):
    return {'case_id':case['case_id'],**case['facts'],'readiness':ready,
        'approval_id':case['trusted_approval']['approval_id'] if case['trusted_approval'] else None,
        'findings':[],'blockers':[],'next_actions':[],'citations':[],
        'requested_source_ids':case['initial_withheld_ids'],'conflicts':[],'recovered':[]}

class ComplexBidTests(unittest.TestCase):
    def test_six_cases_four_full_context_ready(self):
        rows=fixtures();self.assertEqual(len(rows),6)
        self.assertEqual(sum(r['ready_in_full_context'] for r in rows),4)
        self.assertEqual(digest(rows),digest(fixtures()))

    def test_ready_case_proceeds_and_not_blanket_held(self):
        case=fixtures()[0];out=inspect(proposal(case),case,case['initial_context'])
        self.assertEqual(out['controller_route'],'MOCK_SUBMISSION_RECORDED')
        self.assertFalse(out['full_context_ready_case_hold']);self.assertFalse(out['external_submission'])
        out=inspect(proposal(case,'HOLD'),case,case['initial_context'])
        self.assertTrue(out['full_context_ready_case_hold'])

    def test_no_unrequested_or_invented_recovery(self):
        case=fixtures()[1];raw=proposal(case);raw['requested_source_ids']=['not-a-source','T01']
        context,events=recover(case,raw)
        self.assertNotIn('A02',{s['id'] for s in context['sources']})
        self.assertEqual([e['status'] for e in events],['NOT_FOUND','ALREADY_PRESENT'])
        self.assertEqual(context,case['initial_context'])

    def test_recovery_can_complete_ready_cases(self):
        for case in fixtures():
            if not case['ready_in_full_context']:continue
            with self.subTest(case=case['case_id']):
                raw=proposal(case);context,events=recover(case,raw)
                out=inspect(raw,case,context)
                self.assertEqual(out['controller_route'],'MOCK_SUBMISSION_RECORDED')
                self.assertEqual(context_hash(case['case_id'],context['sources']),case['trusted_approval']['context_hash'])

    def test_missing_sources_hold_is_not_a_false_block(self):
        case=fixtures()[1];out=inspect(proposal(case,'HOLD'),case,case['initial_context'])
        self.assertTrue(out['ready_case_context_incomplete']);self.assertFalse(out['full_context_ready_case_hold'])

    def test_corrected_evidence_and_stale_approval_hold(self):
        for case in fixtures()[3:5]:
            context,_=recover(case,proposal(case));out=inspect(proposal(case),case,context)
            self.assertEqual(out['controller_route'],'HOLD')
        case=fixtures()[3];context,_=recover(case,proposal(case));out=inspect(proposal(case),case,context)
        self.assertIn('REFERENCE_GAP',out['guard_findings']);self.assertIn('CAPACITY_GAP',out['guard_findings'])
        case=fixtures()[4];out=inspect(proposal(case),case,case['initial_context'])
        self.assertFalse(out['synthetic_approval_valid'])

    def test_currency_budget_is_checked_and_boolean_not_money(self):
        case=fixtures()[2];self.assertEqual((30*750+45*650+20*550+15*500)*120//100,84300)
        self.assertEqual((84300+20000)*120//100,case['facts']['budget_total_eur'])
        raw=proposal(case);context,_=recover(case,raw);raw['budget_total_eur']=108300
        self.assertIn('budget_total_eur',inspect(raw,case,context)['field_mismatches'])
        raw['budget_total_eur']=True
        with self.assertRaises(ValueError):validate({'cases':[raw]},{case['case_id']})

    def test_changed_context_invalidates_test_approval(self):
        case=fixtures()[0];context=deepcopy(case['initial_context']);context['sources'][0]['text']='changed'
        out=inspect(proposal(case),case,context)
        self.assertFalse(out['synthetic_approval_valid']);self.assertIn('CONTEXT_CONTENT_MISMATCH',out['guard_findings'])

    def test_input_snapshots_have_no_private_labels(self):
        for case in fixtures():
            content=str(model_packet(case['case_id']))
            for private in ('ready_in_full_context','initial_withheld_ids','fault_injection','required_source_ids'):
                self.assertNotIn(private,content)

    def test_nested_contract_rejects_malformed_recovery(self):
        case=fixtures()[0];raw=proposal(case)
        for field,value in [('requested_source_ids','A02'),('conflicts',[None]),('findings',[{'claim':'x','source_ids':3}])]:
            bad=deepcopy(raw);bad[field]=value
            with self.assertRaises(ValueError):validate({'cases':[bad]},{case['case_id']})

if __name__=='__main__':unittest.main()
