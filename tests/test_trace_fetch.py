"""Run metadata locates traces; child spans need not duplicate that metadata."""
from types import SimpleNamespace
import unittest
from unittest.mock import Mock

from tools.phoenix.inspect_trace import fetch


class TraceFetchTests(unittest.TestCase):
    def test_fetch_includes_children_without_run_metadata(self):
        root = {'context': {'trace_id': 'trace-a', 'span_id': 'root'}}
        child = {'context': {'trace_id': 'trace-a', 'span_id': 'child'}}
        query = Mock(side_effect=[[root], [root, child]])
        client = SimpleNamespace(spans=SimpleNamespace(get_spans=query))
        self.assertEqual(fetch(client, 'project', 'run'), [root, child])
        self.assertEqual(query.call_args_list[0].kwargs,
                         {'project_identifier': 'project',
                          'attributes': {'metadata.run_id': 'run'}, 'limit': 10000})
        self.assertEqual(query.call_args_list[1].kwargs,
                         {'project_identifier': 'project', 'trace_ids': ['trace-a'], 'limit': 10000})

    def test_missing_run_does_not_query_unrelated_traces(self):
        query = Mock(return_value=[])
        client = SimpleNamespace(spans=SimpleNamespace(get_spans=query))
        self.assertEqual(fetch(client, 'project', 'missing'), [])
        query.assert_called_once()


if __name__ == '__main__':
    unittest.main()
