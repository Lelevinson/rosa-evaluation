"""Two separate IPC channels: allowlisted agent tools versus oracle scoring."""
import multiprocessing

from rosa_backends.observation_cache import ObservationCache
from .world import serve


class WorldClient:
    def __init__(self, spec, policy='none'):
        context = multiprocessing.get_context('spawn')
        self.agent, child_agent = context.Pipe()
        self.evaluator, child_evaluator = context.Pipe()
        self.process = context.Process(target=serve, args=(child_agent, child_evaluator, spec), daemon=True)
        self.process.start()
        child_agent.close()
        child_evaluator.close()
        self.cache = ObservationCache(policy)

    def request(self, pipe, value):
        pipe.send(value)
        if not pipe.poll(15):
            raise TimeoutError('Mock IPC deadline exceeded')
        return pipe.recv()

    def call(self, name, **args):
        clock = self.request(self.agent, {'operation': 'advance'})
        return self.cache.call(name, args, **clock,
            invoke=lambda name, args: self.request(self.agent, {'operation': 'tool', 'name': name, 'args': args}),
            on_cached=lambda name, args, value: self.request(self.agent,
                {'operation': 'cached_observation', 'name': name, 'args': args, 'value': value}))

    def score(self):
        return self.request(self.evaluator, {'operation': 'score', 'metrics': self.cache.metrics})

    def close(self):
        if self.process.is_alive():
            try:
                self.request(self.evaluator, {'operation': 'close'})
            except (EOFError, OSError, TimeoutError):
                pass
        self.process.join(timeout=2)
        if self.process.is_alive():
            self.process.terminate()
            self.process.join(timeout=2)
        self.agent.close()
        self.evaluator.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
