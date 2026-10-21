# Trace-export environment correction

The scripted native-message ROSA agent and actual parameter read completed.
Export then failed because phoenix.client belongs to the separate Phoenix
environment, not the research environment. No live model requests were made.

Export/audit now use that existing environment directly. A fresh acceptance
records its run ID before execution and retains the exported nested-tool trace.
