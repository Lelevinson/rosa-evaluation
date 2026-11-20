# Prompt-contract live validation with bounded continuation

Qwen: 9/9 correct completed outcomes,34 model requests.
Sol: 4/4 correct completed scoreable outcomes; 5 total attempt rows; 1 censored attempt(s).

Hosted resource ledger: `{"additional_cap": 40, "additional_reserved_calls": 0, "combined_reserved_calls": 13, "original_combined_cap": 72, "prior_reserved_calls": 13}`.
All-attempt costs include the original interrupted attempt. Its unreturned generation has unknown cost, not zero. Its raw failed terminal score is unchanged. Four originally completed outcomes were preserved; only the read-only interrupted cell and unstarted cells were eligible for the continuation.

| Hosted condition | Completed correct | Calls, all attempts | Known input tokens | Known output tokens | Native ops | Invalid attempts |
|---|---:|---:|---:|---:|---:|---:|
| model | 1/1 | 6 | 7233 | 126 | 2 | 0 |
| macro | 2/2 | 5 | 7537 | 137 | 4 | 0 |
| workflow | 1/1 | 2 | 2903 | 55 | 2 | 0 |

All hosted attempt audits: 5/5. Cleanup verified: True.

Overall engineering gate: False. Overall progression gate: False.

This is known-case validation with one run per completed cell. It does not establish a causal prompt effect, broad reliability advantage or an improvement to model weights. Qwen attempted a write without available prerequisite data; ROSA blocked it before dispatch and Qwen corrected its final report. Such outcomes credit the guarded combined system. Additional observation attempts beyond soft retry guidance remain disclosed behavior; original frozen scores are not retrospectively changed.

Keep the initial engineering report, initial live attempt report and this continuation report separate until the user requests the combined discussion package. The held-out pilot remains gated on the completed validation and its own prospective freeze and manual hosted consent.
