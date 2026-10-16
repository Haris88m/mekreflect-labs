from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from observer8.bid_case import FIELD_SOURCE_DEPENDENCIES
from observer8.bid_complex import fixtures
from observer8.bid_handoff import CURRENT_FIELDS, inspect_handoff
from observer8.__main__ import demo, evaluate, illustrative_response, model_packet
from observer8.strict_json import StrictJSONError, dumps, loads


class PublicLabTests(unittest.TestCase):
    def test_source_loss_clears_only_dependent_current_fields(self):
        response = {'current_deadline': '2026-10-30T12:00:00Z',
                    'team_lead_confirmed_days': 10, 'readiness': 'PREPARATION_ONLY'}
        original = deepcopy(response)
        out = inspect_handoff(response, {'T01','A01','B01','C01'},
                              {'T01','A01','B01','C01','E01'}, FIELD_SOURCE_DEPENDENCIES)
        self.assertEqual(response, original)
        self.assertEqual(out['normalised_view']['current_deadline'], response['current_deadline'])
        self.assertIsNone(out['normalised_view']['team_lead_confirmed_days'])
        self.assertEqual(out['normalised_view']['readiness'], 'HOLD')
        self.assertFalse(out['external_actions_permitted'])

    def test_complete_manifest_is_not_semantic_verification_or_submission_authority(self):
        out = inspect_handoff({'readiness':'READY_TO_SUBMIT'}, {'T01'}, {'T01'})
        self.assertFalse(out['external_actions_permitted'])
        self.assertIn('NOT_SEMANTICALLY_CERTIFIED', out['normalised_view']['context_currentness'])
        self.assertEqual(out['normalised_view']['readiness'], 'HOLD')

    def test_incomplete_manifests_rejected(self):
        with self.assertRaises(ValueError):
            inspect_handoff({}, set(), set())
        with self.assertRaises(ValueError):
            inspect_handoff({}, {'T01'}, {'T01'}, {'current_deadline':{'T01'}})
        self.assertEqual(len(CURRENT_FIELDS), 5)

    def test_demo_is_scripted_and_reproducible(self):
        first = demo()
        self.assertEqual(first, demo())
        self.assertEqual(first['execution_mode'], 'SCRIPTED_ORACLE_CONTROL_NOT_AI_EXECUTION')
        routes = [row['recovery_check']['controller_route'] for row in first['cases']]
        self.assertEqual(routes.count('MOCK_SUBMISSION_RECORDED'), 4)
        self.assertEqual(routes.count('HOLD'), 2)
        self.assertFalse(first['external_actions'])

    def test_packets_withhold_missing_document_content(self):
        packet = model_packet('O8-BID-202')
        self.assertNotIn('A02', {s['id'] for s in packet['context']['sources']})
        self.assertIn('A02', {s['id'] for s in packet['context']['source_catalogue']})
        self.assertNotIn('facts', packet)
        with self.assertRaises(ValueError):
            model_packet('actual-client')

    def test_local_evaluator_has_no_unrequested_recovery(self):
        case = fixtures()[1]
        response = illustrative_response(case)
        response['requested_source_ids'] = []
        out = evaluate(case['case_id'], response, 'requested-recovery')
        self.assertEqual(out['retrieval_events'], [])
        self.assertEqual(out['check']['controller_route'], 'HOLD')
        self.assertIn('A02', out['check']['missing_source_ids'])

    def test_packet_contract_envelope_is_accepted_by_cli(self):
        case = fixtures()[0]
        response = illustrative_response(case)
        envelope = {'cases': [response]}
        self.assertEqual(evaluate(case['case_id'], envelope, 'initial'),
                         evaluate(case['case_id'], response, 'initial'))
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary)/'synthetic-response.json'
            path.write_text(json.dumps(envelope), encoding='utf-8')
            result = subprocess.run([sys.executable,'-m','observer8','evaluate',
                                     case['case_id'], str(path)], cwd=root,
                                    text=True, capture_output=True, check=True)
            self.assertEqual(json.loads(result.stdout)['check']['controller_route'],
                             'MOCK_SUBMISSION_RECORDED')

    def test_envelope_cannot_smuggle_duplicate_or_other_case(self):
        case = fixtures()[0]
        response = illustrative_response(case)
        for rows in ([], [response, response], [illustrative_response(fixtures()[1])]):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                evaluate(case['case_id'], {'cases': rows}, 'initial')

    def test_contract_five_finding_limit_is_enforced(self):
        case = fixtures()[0]
        response = illustrative_response(case)
        response['findings'] = [{'claim':'synthetic claim','source_ids':['T01']}] * 5
        evaluate(case['case_id'], response, 'initial')
        response['findings'].append({'claim':'sixth','source_ids':['T01']})
        with self.assertRaisesRegex(ValueError, 'at most five'):
            evaluate(case['case_id'], response, 'initial')

    def test_nonfinite_and_boolean_values_are_not_accepted_as_money(self):
        for text in ('NaN', 'Infinity', '-Infinity'):
            with self.assertRaises(StrictJSONError):
                loads('{"value":'+text+'}')
        with self.assertRaises(StrictJSONError):
            dumps({'value': float('nan')})
        case = fixtures()[0]
        response = illustrative_response(case)
        response['budget_total_eur'] = True
        with self.assertRaises(ValueError):
            evaluate(case['case_id'], response, 'initial')

    def test_cli_executes_without_network_or_dependencies(self):
        root = Path(__file__).resolve().parents[1]
        result = subprocess.run([sys.executable,'-m','observer8','demo'], cwd=root,
                                text=True, capture_output=True, check=True)
        self.assertEqual(len(json.loads(result.stdout)['cases']), 6)

    def test_historical_observations_are_separate_from_this_run(self):
        root = Path(__file__).resolve().parents[1]
        recorded = json.loads((root/'data/recorded-observations.json').read_text())
        self.assertEqual(sum(recorded[k]['actual_hosted_tasks'] for k in
                             ('earlier_pilot','ready_pilot','complex_pilot')), 23)
        self.assertTrue(recorded['synthetic'])
        self.assertIn('Minimized transcription', recorded['evidence_type'])


if __name__ == '__main__':
    unittest.main()
