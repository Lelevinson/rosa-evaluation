"""Separate hardening for future campaigns; NOT used by the frozen live study."""
from .gateway import Gateway


class BoundedGateway(Gateway):
    """Apply the existing native-read budget to write dispatches as well."""

    def write(self, node_name, param_name, param_value):
        if len(self.events) >= self.max_native_reads:
            return self.reject('native_operation_budget_exhausted_before_write')
        return super().write(node_name, param_name, param_value)
