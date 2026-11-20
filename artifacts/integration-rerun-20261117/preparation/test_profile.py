"""Zero-network checks of the additive profile and preserved strict schemas."""
from copy import deepcopy
import json
import unittest

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from pydantic import ValidationError
from rosa_reliability.reference import ReferenceReportArgs
from tool_contract_ollama import ToolContractOllama
from rosa_backends.chat_ollama import ConfiguredChatOllama


def tool(name):
    return {'type':'function','function':{'name':name,'parameters':{'type':'object','properties':{}}}}


class ProfileTests(unittest.TestCase):
    def make(self, model='llama3.1:8b-instruct-q4_K_M'):
        return ToolContractOllama(model=model, num_ctx=8192, num_predict=1024,
            temperature=0, seed=42, use_mmap=True, cache=False)

    def test_schemas_survive_tool_result_and_original_messages_are_preserved(self):
        messages=[SystemMessage(content='Original permissions'),HumanMessage(content='Inspect'),
            AIMessage(content='',tool_calls=[{'id':'read-1','name':'read_state','args':{}}]),
            ToolMessage(content='{"rejected":true}',tool_call_id='read-1',additional_kwargs={'name':'read_state'})]
        before=[m.model_dump() for m in messages]
        llm=self.make()
        params=llm._chat_params(messages,tools=[tool('report_fixture')])
        self.assertIn('report_fixture',params['messages'][1]['content'])
        self.assertEqual(params['messages'][0]['content'],'Original permissions')
        self.assertEqual(params['messages'][-1]['content'],'{"rejected":true}')
        self.assertEqual([m.model_dump() for m in messages],before)
        self.assertEqual(llm._chat_params(messages,tools=[tool('report_fixture')]),params)

    def test_rebinding_uses_only_current_tool_definitions(self):
        llm=self.make(); messages=[HumanMessage(content='Choose a permitted tool')]
        one=llm._chat_params(messages,tools=[tool('first_fixture')])
        two=llm._chat_params(messages,tools=[tool('second_fixture')])
        self.assertIn('first_fixture',one['messages'][0]['content'])
        self.assertNotIn('first_fixture',two['messages'][0]['content'])
        self.assertIn('second_fixture',two['messages'][0]['content'])

    def test_native_guidance_and_nonstreaming_for_both_families(self):
        for name, marker in [('llama3.1:8b-instruct-q4_K_M','"parameters"'),('granite3.3:8b','<|tool_call|>')]:
            params=self.make(name)._chat_params([HumanMessage(content='Inspect')],tools=[tool('probe')],
                options={'num_ctx':8192,'num_predict':73,'temperature':0,'seed':42})
            self.assertFalse(params['stream'])
            self.assertIn(marker,params['messages'][0]['content'])
            self.assertEqual(params['options'],{'num_ctx':8192,'num_predict':73,'temperature':0,'seed':42,'use_mmap':True})

    def test_no_tools_does_not_add_a_schema_message(self):
        params=self.make()._chat_params([HumanMessage(content='Hello')])
        self.assertEqual(len(params['messages']),1)
        self.assertFalse(params['stream'])

    def test_stream_conflict_and_unknown_family_fail_before_network(self):
        with self.assertRaises(ValueError):self.make()._chat_params([HumanMessage(content='Hi')],stream=True)
        with self.assertRaises(ValueError):self.make('unknown:8b')._chat_params([HumanMessage(content='Hi')],tools=[tool('probe')])

    def test_original_backend_and_strict_reporting_unchanged(self):
        base=ConfiguredChatOllama(model='llama3.1:8b-instruct-q4_K_M',use_mmap=True)
        self.assertTrue(base._chat_params([HumanMessage(content='Hello')])['stream'])
        with self.assertRaises(ValidationError):ReferenceReportArgs.model_validate({'classification':'SUCCESS','observation_id':'fixture'})
        with self.assertRaises(ValidationError):ReferenceReportArgs.model_validate({'status':'SUCCESS','observation_id':'fixture','extra':1})
        self.assertEqual(ReferenceReportArgs.model_validate({'status':'UNKNOWN','observation_id':'fixture'}).status,'UNKNOWN')


if __name__=='__main__':unittest.main()
