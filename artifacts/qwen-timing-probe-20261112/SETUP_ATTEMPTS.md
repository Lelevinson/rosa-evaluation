# Retained setup attempts before model dispatch

Date: 2026-11-12.

- hardware-01: server version and digest verified; local payload assertion
  incorrectly expected Ollama API stream=false from LangChain streaming=False.
  Stopped before invocation/reservation. Fixed to preserve actual pinned adapter
  transport behavior; original logs retained.
- hardware-02: PowerShell's case-insensitive variables made startup-loop $attempt
  collide with the validated $Attempt directory parameter. Stopped before client
  launch, model load or inference reservation. Fixed the loop variable name.
- hardware-03 is the next setup attempt. These setup corrections do not increase
  the one-request global inference allowance. No generation has occurred in the
  first two attempts. Both owned server trees were stopped, and logs retained.

These are probe implementation errors, not Qwen model failures or timing results.
