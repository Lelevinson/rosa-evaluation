"""Phase B adapter for Gazebo D (interface: make_model(kwargs) -> chat model), Llama and Granite only.

It is native-schema-v1 unchanged: rosa-research 8713f9b src/rosa_backends/tool_contract_ollama.py
ToolContractOllama (= ToolContractProfile + ConfiguredChatOllama), as frozen for Phase B
(PHASE_B_ITERATION_LOG.md). Nothing here changes prompts, schemas, parsing or settings.
"""
EXPECTED_PROFILE = 'native-schema-v1'


def make_model(kwargs):
    from rosa_backends.tool_contract_ollama import ToolContractOllama, PROFILE_VERSION
    if PROFILE_VERSION != EXPECTED_PROFILE:
        raise RuntimeError('unexpected_tool_contract_profile:' + PROFILE_VERSION)
    if kwargs['model'].partition(':')[0] not in ('llama3.1', 'granite3.3'):
        raise ValueError('native_schema_v1_adapter_is_for_llama_and_granite_only')
    return ToolContractOllama(**kwargs)
