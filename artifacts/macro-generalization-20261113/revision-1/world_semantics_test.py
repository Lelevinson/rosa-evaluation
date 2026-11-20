"""Stage 0 world/transport units; no scripted ROSA or model-turn controls."""
from pathlib import Path
import hashlib
import json
import unittest
from worlds import DOMAINS, create_world

ROOT=Path(__file__).resolve().parent


class WorldSemantics(unittest.TestCase):
    def test_expired_map_lease_is_a_revision_mismatch(self):
        world,actor,observer=create_world('base',false_source='map_lease')
        self.assertEqual(actor.read_group('map_lease',['map_lease_valid']),{'map_lease_valid':False})
        truth=observer.observe()
        self.assertNotEqual(truth['raw_quantities']['map_revision'],truth['raw_quantities']['lease_map_revision'])
        self.assertIs(truth['sources']['map_lease']['map_lease_valid'],False)

    def test_lost_localization_hides_actor_pose_but_not_world_truth(self):
        spec=DOMAINS['base']
        world,actor,observer=create_world('base',false_source='localization')
        with self.assertRaises(TimeoutError): actor.read(spec['node'],list(spec['initial']))
        truth=observer.observe()
        self.assertEqual(truth['pose'],spec['initial'])
        self.assertIs(truth['sources']['localization']['pose_fix_valid'],False)
        self.assertEqual(actor.records[-1]['kind'],'pose_read_timeout')

    def test_base_goto_updates_energy_without_extra_source_acquisition(self):
        spec=DOMAINS['base']
        world,actor,observer=create_world('base')
        initial=observer.observe()['raw_quantities']['battery_fraction']
        actor.write(spec['node'],spec['target'])
        truth=observer.observe()
        self.assertEqual(truth['pose'],spec['target'])
        self.assertLess(truth['raw_quantities']['battery_fraction'],initial)
        self.assertEqual([r['kind'] for r in world.records()],['movement_dispatch'])
        self.assertEqual(world.records()[0]['domain_command'],'goto')

    def test_partial_effects_differ_between_domains(self):
        for domain,spec in DOMAINS.items():
            with self.subTest(domain=domain):
                world,actor,observer=create_world(domain,write_effect='partial')
                actor.write(spec['node'],spec['target'])
                pose=observer.observe()['pose']
                self.assertNotEqual(pose,spec['target'])
                if domain=='arm':
                    self.assertEqual(pose['pitch'],spec['target']['pitch'])
                    self.assertEqual(pose['yaw'],spec['initial']['yaw'])
                else:
                    self.assertEqual(pose['x_m'],spec['target']['x_m'])
                    self.assertEqual(pose['y_m'],spec['target']['y_m'])
                    self.assertEqual(pose['heading_fraction'],spec['initial']['heading_fraction'])

    def test_read_only_grant_prevents_dispatch(self):
        for domain,spec in DOMAINS.items():
            with self.subTest(domain=domain):
                world,actor,observer=create_world(domain,write_authorized=False)
                self.assertIsNotNone(actor.validate_write(spec['node'],spec['target']))
                with self.assertRaises(ValueError): actor.write(spec['node'],spec['target'])
                self.assertEqual(observer.observe()['dispatches'],0)
                self.assertEqual(world.records(),[])


if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(WorldSemantics))
    out={'pass':result.wasSuccessful(),'test_methods':result.testsRun,'model_requests':0,
         'scope':'Stage0 world/transport unit checks; not Stage1 public-tool/fake-model control suite',
         'world_source_sha256':hashlib.sha256((ROOT/'worlds.py').read_bytes()).hexdigest(),
         'errors':len(result.errors),'failures':len(result.failures)}
    (ROOT/'world-semantics-results.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    raise SystemExit(0 if result.wasSuccessful() else 1)
