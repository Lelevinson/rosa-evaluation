"""Stage 0 observer unit proof; no model/ROSA path, Phoenix, or robot execution."""
from copy import deepcopy
import json
import hashlib
from pathlib import Path
import unittest

from worlds import DOMAINS, create_world

ROOT = Path(__file__).resolve().parent


class SeparationTests(unittest.TestCase):
    evidence = []

    def test_corrupted_actor_read_cannot_change_truth(self):
        for domain, spec in DOMAINS.items():
            with self.subTest(domain=domain):
                world, actor, observer = create_world(domain, corrupt_read=True)
                returned = actor.read(spec['node'], list(spec['initial']))
                observed = observer.observe()
                self.assertNotEqual(returned, observed['pose'])
                self.assertEqual(observed['pose'], spec['initial'])
                self.assertIsNot(actor.state, observer.state)
                self.assertIsNot(actor.records, observer.records)
                self.assertIsNot(actor._channel, observer._channel)
                self.assertFalse(hasattr(observer._channel, 'command'))
                self.evidence.append({'domain': domain, 'check': 'corrupted_actor_read',
                    'actor': deepcopy(returned), 'observer': deepcopy(observed), 'pass': True})

    def test_dropped_ack_does_not_hide_actual_movement(self):
        for domain, spec in DOMAINS.items():
            with self.subTest(domain=domain):
                world, actor, observer = create_world(domain, drop_ack=True)
                actor.read(spec['node'], list(spec['initial']))
                before = deepcopy(actor.state)
                with self.assertRaises(TimeoutError):
                    actor.write(spec['node'], spec['target'])
                observed = observer.observe()
                self.assertEqual(actor.state, before)  # Actor cache remains stale.
                self.assertEqual(observed['pose'], spec['target'])
                self.assertEqual(observed['dispatches'], 1)
                self.evidence.append({'domain': domain, 'check': 'dropped_ack_after_effect',
                    'actor_stale_state': before, 'observer': observed, 'dispatches': actor.writes, 'pass': True})

    def test_actor_mutation_cannot_mutate_observer_or_world(self):
        for domain, spec in DOMAINS.items():
            with self.subTest(domain=domain):
                world, actor, observer = create_world(domain)
                actor_result = actor.read(spec['node'], list(spec['initial']))
                observer_result = observer.observe()
                old_records, old_state = deepcopy(observer.records), deepcopy(observer.state)
                field = next(iter(spec['initial']))
                actor.state[spec['node']][field] = 999
                actor.records[0]['values'][field] = 888
                actor_result[field] = 777
                self.assertEqual(observer.records, old_records)
                self.assertEqual(observer.state, old_state)
                observer_result['pose'][field] = 666
                self.assertEqual(observer.state, old_state)
                self.assertEqual(observer.records, old_records)
                self.assertEqual(observer.observe()['pose'], spec['initial'])
                self.evidence.append({'domain': domain, 'check': 'no_mutable_aliases', 'pass': True})

    def test_actor_unavailability_does_not_disable_observer(self):
        for domain, spec in DOMAINS.items():
            with self.subTest(domain=domain):
                source, field = spec['checks'][0]
                world, actor, observer = create_world(domain, pose_unavailable=True, unavailable_source=source)
                with self.assertRaises(TimeoutError): actor.read(spec['node'], list(spec['initial']))
                with self.assertRaises(TimeoutError): actor.read_group(source,[field])
                observed = observer.observe()
                self.assertEqual(observed['pose'], spec['initial'])
                self.assertIs(observed['sources'][source][field], True)
                self.evidence.append({'domain':domain, 'check':'actor_unavailable_observer_available', 'pass':True})


if __name__ == '__main__':
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(SeparationTests))
    report = {'stage':'Stage 0 observer-separation unit proof', 'tests':result.testsRun,
              'domain_checks':len(SeparationTests.evidence), 'pass':result.wasSuccessful(),
              'failures':len(result.failures), 'errors':len(result.errors),
              'model_requests':0, 'Stage1_scripted_controls_run':False,
              'world_source_sha256':hashlib.sha256((ROOT/'worlds.py').read_bytes()).hexdigest(),
              'test_source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'independence':'separate state objects, transport channels and records over one authority; same authorship/sensor technology',
              'evidence':SeparationTests.evidence}
    (ROOT/'observer-separation-results.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    raise SystemExit(0 if result.wasSuccessful() else 1)
