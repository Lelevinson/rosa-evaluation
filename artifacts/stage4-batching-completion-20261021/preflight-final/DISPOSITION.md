# CLI discovery readiness failure

The private evaluator reset succeeded, but the first CLI get ran before its
separate daemon graph discovered the new node. Its raw stderr, Node not found,
is preserved. No live model calls occurred. Cleanup stopped the test nodes.

Environment startup now waits for the CLI node graph to list both test nodes;
this checks graph readiness without reading parameter values. Fresh acceptance
uses preflight-accepted. The existing 72 passing test record is reused.
