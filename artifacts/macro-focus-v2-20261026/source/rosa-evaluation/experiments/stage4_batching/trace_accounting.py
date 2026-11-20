"""Count native operations by explicit provenance, independent of span nesting."""


def counts(spans):
    tools = [s for s in spans if s['span_kind'] == 'TOOL']
    native = [s for s in tools if 'stage4.actor' in s['attributes']]
    model = [s for s in tools if 'stage4.actor' not in s['attributes']]
    return {'native_tool_spans': len(native), 'model_tool_spans': len(model),
            'native_actors': [s['attributes']['stage4.actor'] for s in native],
            'model_tool_names': [s['name'] for s in model]}
