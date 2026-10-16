"""Server-side packet completeness guard, separate from LLM recommendations."""
from __future__ import annotations
from copy import deepcopy

CURRENT_FIELDS=('current_deadline','contract_cap_eur','verified_reference_count',
                'team_lead_confirmed_days','budget_total_eur')


def inspect_handoff(response: dict, available_source_ids: set[str], required_source_ids: set[str],
                    field_dependencies: dict[str,set[str]] | None = None) -> dict:
    """Protect structured consumers without reading evaluator outcome labels.

    Completeness does NOT prove semantic correctness. This checks whether the
    trusted ingestion manifest's required sources reached the receiving worker.
    """
    if type(response) is not dict or not required_source_ids:
        raise ValueError('manager object and nonempty trusted source manifest required')
    if any(type(value) is not str or not value for value in available_source_ids | required_source_ids):
        raise ValueError('source IDs must be nonempty strings')
    missing=sorted(required_source_ids-available_source_ids)
    issues=[]
    view=deepcopy(response)
    dependencies=field_dependencies or {key:required_source_ids for key in CURRENT_FIELDS}
    if set(dependencies)!=set(CURRENT_FIELDS) or any(not ids or not ids <= required_source_ids for ids in dependencies.values()):
        raise ValueError('every current field requires nonempty dependencies within the trusted source manifest')
    per_field_missing={key:sorted(ids-available_source_ids) for key,ids in dependencies.items()}
    recorded={}
    for key, absent in per_field_missing.items():
        if absent:
            recorded[key]=view.get(key)
            view[key]=None
    view['field_currentness']={key:{'missing_source_ids':absent,
        'status':'NOT_ESTABLISHED' if absent else 'REQUIRED_RECORDS_PRESENT_NOT_SEMANTICALLY_CERTIFIED'}
        for key,absent in per_field_missing.items()}
    if missing:
        issues.append('INCOMPLETE_REQUIRED_SOURCE_BUNDLE')
        view['unverified_values_from_received_records']=recorded
        view['context_currentness']='NOT_ESTABLISHED'
    else:
        view['context_currentness']='REQUIRED_RECORDS_PRESENT_NOT_SEMANTICALLY_CERTIFIED'
    readiness=response.get('readiness')
    if readiness not in {'READY_TO_SUBMIT','PREPARATION_ONLY','HOLD'}:
        issues.append('INVALID_READINESS_LABEL')
    if readiness=='READY_TO_SUBMIT':
        # A model's own approval statement is never a human approval token.
        issues.append('NO_AUTHENTICATED_SUBMISSION_CAPABILITY_IN_THIS_TEST')
    if issues:
        view['readiness']='HOLD'
    return {'missing_required_source_ids':missing,'guard_findings':issues,
            'normalised_view':view,'external_actions_permitted':False,
            'scope':'Source-completeness and structured-field hygiene only; not content verification or a production authorisation service.'}
