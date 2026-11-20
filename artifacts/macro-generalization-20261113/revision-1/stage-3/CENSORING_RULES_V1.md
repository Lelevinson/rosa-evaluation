# Analysis-layer censoring rules, version 1

Date: 2026-11-14. Written before held-out inference; awaiting the G-g freeze. No scorer modification.

INFRA_CENSORED_PRE_OUTPUT means a provider/transport failure with no completed response in that call, before any tool execution, native operation or dispatch in the trial. G1r1-dev-012-primitives satisfies this definition.

INFRA_CENSORED_POST_ACTION means such a failure after at least one tool execution, native operation or dispatch. Preserve the observer record and never replay the task or an uncertain command. Record the activity that preceded the failed call rather than guessing from later activity. For a recovered failure, an explicit pre-failure activity record is required; absent that record the analysis stops for an unclassified chronology rather than inventing PRE/POST status.

Analysis overlay component columns (selection, execution, report and goal) are NOT_EVALUABLE for both classes. The raw scorer flags and primary scores remain unchanged. A budget deadline, output-length ending, wrong choice, invalid tool call or scorer/harness defect is not automatically infrastructure censoring.

- V1 reports operational outcomes over all scheduled attempts: correct completed, incorrect evaluable, infrastructure-censored, and unstarted. Retain actual denominators.
- V2 reports correctness over evaluable attempts only. Matched-success efficiency excludes an entire pair if either arm is censored, unstarted or unsuccessful. Report exclusions per domain/depth and separate censorship from other unmatched-success exclusions.
- V3 counts censored attempts as failures and retains the scheduled denominator. Unstarted attempts remain explicitly labeled, not invented model failures. An incomplete campaign cannot support a completed-campaign prediction claim.
- Prediction status follows V2. If V3 changes its status in either direction, report Uninformative and show both. Eight or more censored trials in the planned 76-trial backend run flag it operationally compromised and make its prediction statuses Uninformative unless a separately documented owner decision supersedes this rule after the data.
- Retry rules remain unchanged: explicit HTTP 502/503/504 only, existing exclusion terms, one retry/logical call, three reserve attempts/backend, one-second backoff, every physical attempt charged. In-stream errors do not qualify. No failed task or command is replayed.
- The pair gap is the absolute difference between the earliest retained local-trace start timestamp in each arm. Flag a gap strictly greater than 30 minutes. Report the basis and raw seconds; do not call this an exact wall-clock task-start measurement.
- Failed-call usage is unknown unless actually returned. Never assign zero provider work merely because no completed response was received.

The analysis implementation is a candidate, not a frozen executable: the requested P1-prime/P6 definitions are missing. Existing P1-P5 logic is diagnostic only on Stage 2 dev data; no prediction is adjudicated here.
