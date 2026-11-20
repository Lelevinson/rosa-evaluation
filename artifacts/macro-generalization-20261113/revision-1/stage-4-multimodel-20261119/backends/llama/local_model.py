"""Unchanged configured Ollama adapter plus bounded physical-call observation."""
from copy import deepcopy
import time
from pydantic import PrivateAttr
from rosa_backends.chat_ollama import ConfiguredChatOllama
from recovery import transient


class LocalObservation:
    def __init__(self):
        self.error_metadata_records = []

    def release_transient_failure(self, error):
        if not transient(error):
            raise RuntimeError('ineligible_local_transport_retry')
        # The Ollama client has no sticky unavailable flag to clear.


class MeasuredOllama(ConfiguredChatOllama):
    _records: list = PrivateAttr(default_factory=list)
    _observation: object = PrivateAttr(default=None)

    @property
    def request_records(self):
        return deepcopy(self._records)

    def observe_with(self, observation):
        self._observation = observation
        return self

    def _chat_params(self, messages, stop=None, **kwargs):
        params = super()._chat_params(messages, stop=stop, **kwargs)
        if self._records:
            self._records[-1]['effective_settings'] = {
                'model': params.get('model'), 'think': params.get('think'),
                'stream': params.get('stream'), 'options': deepcopy(params.get('options'))}
        return params

    def _generate(self, *args, **kwargs):
        started = time.monotonic()
        record = {'physical_request_index': len(self._records) + 1, 'status': 'STARTED'}
        self._records.append(record)
        try:
            result = super()._generate(*args, **kwargs)
            generation = result.generations[0]
            record.update(status='RETURNED', usage=deepcopy(generation.message.usage_metadata),
                generation_info=deepcopy(generation.generation_info),
                tool_call_count=len(generation.message.tool_calls or []))
            return result
        except Exception as error:
            status = getattr(error, 'status_code', None)
            record.update(status='ERROR', error_type=type(error).__name__, http_status=status)
            # Only observed transport surfaces establish censoring evidence.
            if self._observation is not None:
                kind = type(error).__name__
                surface = ('HTTP' if isinstance(status, int) else
                    'TIMEOUT' if kind in ('ReadTimeout', 'ConnectTimeout', 'TimeoutError') else
                    'TRANSPORT' if kind in ('ConnectError', 'ConnectionError', 'URLError') else None)
                if surface:
                    self._observation.error_metadata_records.append({
                        'failure_surface': surface, 'http_status': status,
                        'error_type': kind[:64], 'elapsed_ms': int((time.monotonic() - started) * 1000)})
            raise
        finally:
            record['wall_seconds'] = time.monotonic() - started


def configured_model(endpoint, observation):
    return MeasuredOllama(model='llama3.1:8b-instruct-q4_K_M', base_url=endpoint,
        num_ctx=8192, num_predict=1024, temperature=0, seed=42, use_mmap=True,
        streaming=False, reasoning=False, cache=False,
        client_kwargs={'timeout': 180}).observe_with(observation)
