# Live validation R2: setup amendment after zero-inference R1 abort

R1 stopped at its first independent home-reset check before any model inference.
Keep that zero-inference failure, simulator logs, revoked OAuth session and R1
analysis intact. This is not a second retry after another hosted-service failure.
R2 refuses to run if R1 used even one model request or lacks clean teardown.

The installed simulator spawns elbow_joint=0 and wrist_2_joint=0, whereas the
documented benchmark HOME specifies1.57 and-1.57 respectively. The first setup
trajectory in R1 hit a controller path-tolerance violation (joint2 error about
0.202 versus its0.2 tolerance) and the independent home reset correctly failed.
This demonstrates a setup problem; timing/initialization details can affect it.
It is not evidence of a model failure or justification for loosening tolerances.

Small simulator-only amendment: generated copy of the installed top-level
ur_gz.urdf.xacro, adding ONE initial_positions attribute to the existing
ur_ros2_control macro invocation. That existing macro parameter is passed the
documented six-joint HOME. Installed packages, all geometry, physics/controller
settings, tolerances, tool schemas, actor transport, inference settings, model
prompts, scoring and per-trial limits remain unchanged. Spawn readiness now also
requires an independent fresh HOME observation. Startup service polling is
throttled to50ms; no command is retried. Old frozen files are not edited.

Separate zero-model validation passed2 unit methods,3 independent cold starts,
18 deterministic control cases, and three clean simulator shutdowns. Source
copies/digests, generated/original descriptions, independent observations and
control results are under artifacts/simulator-home-v1-preflight-20261026.
The description-diff unit check confirms that only the initial_positions
attribute changed. No general claim of collision-safe simulation is made;
the installed DART mesh-collision warnings remain a limitation.

R2 retains the original R1-selected indices4..8: the one read-only service-
censored trial and four unstarted cells. No completed model outcome is replaced.
Same original query/agent/scorer/controller, same fresh six deterministic controls,
same local/input/Phoenix audits. Apply the HomeSpawnSimulator only in the separate
coordinator scope; restore that scope even on error. The initial Qwen and four
completed Sol cells all began after independent HOME resets; disclose that their
outside-trial initialization route differed from R2. These are known-case
engineering results, not a causal treatment effect or confirmatory comparison.

At most40 additional hosted requests, maximum53 combined with the initial13 and
R1's0. Original72 ceiling and4500 cumulative active seconds remain enforced;
R1 setup time is included. Separate simulator-only engineering diagnostics are
recorded outside model-trial costs. No further service-failure retry loop.
All-attempt costs include the initial unknown-cost unreturned request.

Normal scope checks, manual initial consent, memory-only renewal and revocation
remain mandatory. R1's session was already revoked after setup failure; obtain
fresh manual consent only after the zero-model setup proof and source freeze.
No credential persistence or OAuth implementation changes. Save outcomes and
stop on another environment/service/audit failure. The fresh pilot stays gated
until all18 scoreable original validation cells and every attempt audit pass.
