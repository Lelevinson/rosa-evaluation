"""Prospective scoring adds dispatch/fault coverage; never changes old scores."""
from experiments.workflow_reference_v1.runner import score as previous_score


def score(session, spec, transport, answer, claims, skills, tolerance, actual=None):
    result = previous_score(session, spec, transport, answer, claims, skills, tolerance, actual)
    dispatches = [r for r in transport.records if r['kind'] in ('write', 'trajectory_request')]
    targets = skills[spec['skill']]['/ur5e']
    correct_commands = bool(dispatches) and all(set(r.get('requested', {})) == set(targets) and
        all(abs(r['requested'][k] - v) < 1e-9 for k, v in targets.items()) for r in dispatches)
    transient_seen = any(r.get('transient_after_write') for r in transport.records)
    missing_seen = any(r['kind'] == 'observation_timeout' for r in transport.records)
    fault_exercised = (correct_commands if spec['fault'] == 'drop' else
                       transient_seen and correct_commands if spec['fault'] == 'transient_after' else
                       missing_seen if spec['fault'] == 'missing' else None)
    coverage = len(dispatches) == spec['required_dispatches'] and (
        correct_commands if spec['required_dispatches'] else True) and fault_exercised is not False
    result.update(legacy_outcome_contract_pass=result['pass'], dispatch_count=len(dispatches),
        required_dispatches=spec['required_dispatches'], requested_goal_command_attempted=correct_commands,
        injected_fault_exercised=fault_exercised, coverage_pass=coverage,
        transient_observation_failure_seen=transient_seen,
        pass_with_required_coverage=bool(result['pass'] and coverage))
    result['pass'] = result['pass_with_required_coverage']
    return result
