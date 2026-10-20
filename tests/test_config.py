import tempfile
from pathlib import Path
import unittest

from experiments.config import (
    ROOT, checkout, configured_path, load_config, phoenix_url,
    run_dir, tool_output_dir, tool_state_dir, validation_dir,
)
from tools.phoenix import config as phoenix_config


class ConfigurationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / 'evaluation'
        self.root.mkdir()
        (self.root / 'config.toml').write_text((ROOT / 'config.toml').read_text())
        self.tool = self.root / 'tools/phoenix'
        self.tool.mkdir(parents=True)
        (self.tool / 'config.toml').write_text((ROOT / 'tools/phoenix/config.toml').read_text())

    def test_local_override_preserves_unmodified_defaults(self):
        (self.tool / 'config.local.toml').write_text('[phoenix]\nurl = "http://localhost:6007"\n')
        config = load_config(self.tool)
        self.assertEqual(config['phoenix']['project'], 'rosa-local')
        self.assertEqual(phoenix_url(self.root), 'http://localhost:6007')

    def test_tool_settings_match_runner_without_importing_runner(self):
        (self.tool / 'config.local.toml').write_text('[phoenix]\nurl = "http://localhost:6007"\n')
        self.assertEqual(phoenix_config.phoenix_url(self.tool), phoenix_url(self.root))
        self.assertEqual(phoenix_config.phoenix_project(self.tool), 'rosa-local')

    def test_tool_paths_keep_existing_data_and_result_locations(self):
        self.assertEqual(phoenix_config.tool_state_dir('phoenix', self.tool), self.root / '.local/phoenix')
        self.assertEqual(phoenix_config.tool_output_dir('run-1', 'phoenix', self.tool),
                         tool_output_dir('run-1', 'phoenix', self.root))

    def test_relative_and_absolute_output_paths(self):
        self.assertEqual(configured_path('results', self.root), self.root / 'results')
        destination = self.root / 'separate-storage'
        (self.root / 'config.local.toml').write_text(f'[paths]\nresults = "{destination}"\n')
        self.assertEqual(run_dir('run-1', self.root), destination / 'runs/run-1')

    def test_tools_share_run_identity_without_overwriting_each_other(self):
        first = tool_output_dir('run-1', 'phoenix', self.root)
        second = tool_output_dir('run-1', 'future-tool', self.root)
        self.assertEqual(first.parent, second.parent)
        self.assertNotEqual(first, second)
        self.assertNotEqual(tool_state_dir('phoenix', self.root), first)
        self.assertNotEqual(validation_dir('suite-1', 'phoenix', self.root), first)

    def test_output_identifiers_cannot_escape_their_directory(self):
        for value in ('../outside', '..', '/tmp/outside', 'a/b'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                tool_output_dir(value, 'phoenix', self.root)
        with self.assertRaises(ValueError):
            tool_output_dir('run-1', '../outside', self.root)

    def test_baseline_configuration_does_not_require_a_baseline_directory(self):
        self.assertEqual(checkout('research', self.root), self.root.parent / 'rosa-research')
        self.assertFalse(checkout('baseline', self.root).exists())
        with self.assertRaisesRegex(ValueError, 'Unknown checkout'):
            checkout('missing', self.root)

    def test_local_phoenix_cannot_accidentally_bind_a_remote_address(self):
        for url in ('http://0.0.0.0:6006', 'http://example.com:6006', 'http://user:pass@localhost:6006', 'http://localhost:6006/path'):
            (self.tool / 'config.local.toml').write_text(f'[phoenix]\nurl = "{url}"\n')
            with self.subTest(url=url), self.assertRaises(ValueError):
                phoenix_url(self.root)


if __name__ == '__main__':
    unittest.main()
