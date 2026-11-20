# Protected-source decision

Date: **2026-11-15**. The owner selected **Keep protected source unchanged**.

The proposed optional HTTP metadata hook remains unapplied. No authentication, parser, request-body, retry or SafeError change is authorized. The existing zero-network boundary findings remain evidence: an outer G1 wrapper can observe parsed stream events, but the unchanged HTTP helper discards some requested provider fields before returning a sanitized exception.

This decision is not a waiver of A2's field requirements or a passing instrumentation gate. G-c remains BLOCKED under the supplied Stage 3 protocol. A future decision to narrow the required observability would need an explicit dated methodological amendment before the freeze; no such decision is assumed here. Unknown fields remain not recorded rather than reconstructed from guesses.

The owner separately authorized GPT-6 Astra to conduct a real adversarial scorer review. That work can proceed independently of G-c. It is labeled separate-model review and does not replace the uninvolved person's clarification review. No model-driven robotics experiment, OAuth request, Stage 4 run, Git action or upload is authorized by these decisions.
