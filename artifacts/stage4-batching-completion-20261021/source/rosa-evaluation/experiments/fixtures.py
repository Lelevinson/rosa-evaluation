"""Small deterministic fixture: actual LangChain dispatch, no network or ROS CLI."""
from collections import deque
import time
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.tools import tool
from pydantic import PrivateAttr


class ScriptedModel(BaseChatModel):
    _messages: deque = PrivateAttr()

    def __init__(self, steps):
        super().__init__()
        self._messages = deque([
            AIMessage(content='', tool_calls=[{'name': name, 'args': args,
                      'id': f'fixture-{i}', 'type': 'tool_call'}])
            for i, (name, args) in enumerate(steps)
        ] + [AIMessage(content='DONE')])

    @property
    def _llm_type(self):
        return 'scripted-no-network'

    def bind_tools(self, tools, **kwargs):
        return self

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        return ChatResult(generations=[ChatGeneration(message=self._messages.popleft())])


def make_fixture(case):
    entries = []

    @tool
    def fixture_read(value: int) -> dict:
        """Return a supplied integer using ordinary internal Python operations."""
        entries.append('fixture_read')
        return dict(value=int(value))

    @tool
    def fixture_fail() -> str:
        """Raise an intentional execution exception."""
        entries.append('fixture_fail')
        raise RuntimeError('controlled tool failure')

    @tool
    def fixture_report_error() -> dict:
        """Return a semantic failure without raising."""
        entries.append('fixture_report_error')
        return {'error': 'controlled application failure'}

    @tool
    def fixture_nested() -> dict:
        """Invoke a decorated tool internally."""
        entries.append('fixture_nested')
        return fixture_read.invoke({'value': 7})

    @tool
    def fixture_slow() -> str:
        """Simulate an interrupted tool."""
        time.sleep(20)
        return 'finished'

    cases = {
        'interrupted': [('fixture_slow', {})],
        'success': [('fixture_read', {'value': 7}), ('fixture_read', {'value': 8})],
        'execution-error': [('fixture_fail', {})],
        'validation-error': [('fixture_read', {'value': 'not-an-integer'})],
        'reported-error': [('fixture_report_error', {})],
        'nested': [('fixture_nested', {})],
        'unknown-tool': [('fixture_missing', {})],
    }
    return ScriptedModel(cases[case]), [fixture_read, fixture_fail, fixture_report_error, fixture_nested, fixture_slow], entries
