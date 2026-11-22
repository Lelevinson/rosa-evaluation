"""F1 study-only wording wrapper (W1 + W2). No change to frozen or protected source.

Two arms share one harness:
  wording='base' -> the frozen rosa_reliability.macro_agent.MacroROSA, used unchanged.
  wording='new'  -> F1MacroROSA, a subclass that changes only model-visible TEXT:
      * W1a: every state_change catalogue entry gains a 'macro_routine' description;
      * W1b + W2: two sentences appended to the frozen system contract.
The program objects (invocation, session, tools, guards, budgets, scorer input
snapshot) are the frozen ones. The scorer reads invocation.snapshot()['catalogue'],
which this wrapper never touches. Every sentence is justified line by line in
artifacts/f1-catalogue-wording-20261121/WORDING_DIFF.md.

The wording is macro-condition only: the routine text is false for primitives,
so make_agent() refuses any other mode.
"""
from copy import deepcopy
import json

WORDING_REVISION = 'f1-w-r0'  # dev revisions (max 2) bump this and are logged in DEV_REVISION_LOG.md

# W1a: appended to each state_change catalogue entry (macro condition only).
MACRO_ROUTINE = (
    'select_skill runs this routine itself: it reads the current target coordinates first; '
    'if any coordinate is unavailable it writes nothing; if already at the target it skips the write; '
    'otherwise it writes the target once; then it verifies with a fresh observation. '
    'It does not read any readiness check.')

# W1b: one system sentence.
W1_SYSTEM = (
    'If the user goal is a permitted movement, select that movement skill directly: in the macro '
    'condition its routine reads the current target coordinates itself before any write. Select an '
    'inspection skill only when the user asks only to inspect; a task can select only one skill.')

# W2: one system sentence.
W2_SYSTEM = (
    'If the request is ambiguous, reply in plain text with one clarifying question and call no tool; '
    'that reply ends the task without a report.')

SYSTEM_ADDITION = W1_SYSTEM + ' ' + W2_SYSTEM


def w1_catalogue(catalogue):
    """Return a copy of the frozen public catalogue with W1a added to state_change entries only."""
    result = deepcopy(catalogue)
    for entry in result.values():
        if entry.get('kind') == 'state_change':
            entry['macro_routine'] = MACRO_ROUTINE
    return result


def _wrapper_class():
    from langchain_core.messages import SystemMessage
    from langchain_core.prompts import ChatPromptTemplate
    from rosa_reliability.macro_agent import MacroROSA
    from rosa_reliability.prompt_contract import bounded_contract

    class F1MacroROSA(MacroROSA):
        """Text-only override of MacroROSA; routines, guards and budgets are inherited unchanged."""

        def _get_prompts(self, robot_prompts=None):
            template = super()._get_prompts(robot_prompts)
            first = template.messages[0]
            if not isinstance(first, SystemMessage) or first.content != bounded_contract(self.tool_names):
                raise RuntimeError('f1_wrapper_expected_the_frozen_bounded_contract_first')
            return ChatPromptTemplate.from_messages([
                SystemMessage(content=first.content + ' ' + SYSTEM_ADDITION), *template.messages[1:]])

        def invoke(self, query):
            # Same construction as MacroROSA.invoke (macro_agent.py:115-120), with the W1a catalogue.
            request = query + '\nPublic authorized skill catalogue: ' + json.dumps(
                w1_catalogue(self.macro_invocation.catalogue), sort_keys=True)
            return super(MacroROSA, self).invoke(request)

    return F1MacroROSA


def agent_class(wording):
    if wording == 'base':
        from rosa_reliability.macro_agent import MacroROSA
        return MacroROSA
    if wording == 'new':
        return _wrapper_class()
    raise ValueError('wording_must_be_base_or_new')


def make_agent(wording, model, invocation, **kwargs):
    if invocation.mode != 'macro':
        raise ValueError('f1_wording_is_macro_condition_only')
    return agent_class(wording)(model, invocation, **kwargs)
