"""Offline public lab. Demonstrations are scripted, never fresh model results."""
from __future__ import annotations

import argparse
from copy import deepcopy
from pathlib import Path

from .bid_complex import CONTRACT, fixtures, inspect, recover, validate
from .operational import suite
from .strict_json import dumps, load


def get_case(identifier: str) -> dict:
    for case in fixtures():
        if case['case_id'] == identifier:
            return case
    raise ValueError('Unknown synthetic case ID')


def model_packet(identifier: str) -> dict:
    """Export source context, never evaluator facts, labels or hidden contents."""
    return {
        'execution_mode': 'SYNTHETIC_INPUT_ONLY_NO_MODEL_EXECUTION',
        'contract': CONTRACT,
        'context': deepcopy(get_case(identifier)['initial_context']),
    }


def illustrative_response(case: dict) -> dict:
    """An oracle fixture for control testing, explicitly not an AI response."""
    return {
        'case_id': case['case_id'], **case['facts'],
        'readiness': 'READY_TO_SUBMIT',
        'approval_id': case['trusted_approval']['approval_id'] if case['trusted_approval'] else None,
        'findings': [], 'blockers': [], 'next_actions': [], 'citations': [],
        'requested_source_ids': case['initial_withheld_ids'], 'conflicts': [], 'recovered': [],
    }


def demo() -> dict:
    rows = []
    for case in fixtures():
        response = illustrative_response(case)
        recovered, events = recover(case, response)
        rows.append({
            'case_id': case['case_id'], 'complication': case['label'],
            'initial_check': inspect(response, case, case['initial_context']),
            'source_retrieval': events,
            'recovery_check': inspect(response, case, recovered),
        })
    return {
        'execution_mode': 'SCRIPTED_ORACLE_CONTROL_NOT_AI_EXECUTION',
        'purpose': 'Show how the controller behaves with authored expected facts. Not a model benchmark.',
        'external_actions': False, 'cases': rows,
    }


def evaluate(identifier: str, response: dict, phase: str) -> dict:
    """Evaluate user-supplied JSON; no provider calls, execution or auto-repair."""
    case = get_case(identifier)
    # The worker contract returns an envelope; accept it without wrapping twice.
    # Keep direct single-case objects useful for manual local inspection too.
    if type(response) is dict and 'cases' in response:
        validate(response, {identifier})
        response = response['cases'][0]
    validate({'cases': [response]}, {identifier})
    context = case['initial_context']
    events = []
    if phase == 'requested-recovery':
        context, events = recover(case, response)
    return {
        'execution_mode': 'LOCAL_EVALUATION_OF_SUPPLIED_JSON',
        'response_origin': 'Caller supplied; not independently authenticated as model output',
        'retrieval_events': events,
        'check': inspect(response, case, context),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('controls', help='Run 12 scripted fixtures under three policies')
    commands.add_parser('demo', help='Show six scripted complex-case controls')
    packet = commands.add_parser('packet', help='Print a synthetic model input without evaluator labels')
    packet.add_argument('case_id')
    check = commands.add_parser('evaluate', help='Inspect one supplied JSON response offline')
    check.add_argument('case_id')
    check.add_argument('response', type=Path)
    check.add_argument('--phase', choices=['initial', 'requested-recovery'], default='initial')
    args = parser.parse_args(argv)
    try:
        if args.command == 'controls':
            result = suite()
        elif args.command == 'demo':
            result = demo()
        elif args.command == 'packet':
            result = model_packet(args.case_id)
        else:
            result = evaluate(args.case_id, load(args.response), args.phase)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    print(dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
