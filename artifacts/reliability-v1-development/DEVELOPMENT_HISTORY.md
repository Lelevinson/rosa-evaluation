# Pre-live development history

These are development attempts, not additional live trials or replacements for
failed model results. The live source was frozen only after the prerequisites
passed; there were no live model requests before that freeze.

- Gazebo probe 1 failed before observing a joint: JointTransport created its
  own rclpy Context but spin_once implicitly requested the uninitialized global
  executor. The empty rows and owned-child cleanup are retained in
  gazebo-probe-1/deterministic.json. The development traceback identified
  `TypeError: 'NoneType' object does not support the context manager protocol`.
- The transport was fixed to use an explicit SingleThreadedExecutor for each
  context. Probe 2 then independently observed three commanded positions and
  correctly detected a deliberately suppressed command. Its full observations
  and child-process cleanup are retained in gazebo-probe-2/.
- Focused checks were refined before freezing to cover null observations and
  an actual ROSA controlled-stop callback/span path. The final unit-tests.log
  and integration-tests.log record eight focused tests and three integration
  tests, including sixteen deterministic fixture/arm controls.
- The first detached operator launcher sourced ROS under `set -u`, causing an
  unset AMENT_TRACE_SETUP_FILES shell-variable error before sign-in or model
  requests. The launcher was corrected without changing frozen runtime code.
  Its failure log and supervisor record are retained at the campaign root as
  pipeline-startup-failure-1.log and supervisor-startup-failure-1.json.
- The hosted model subsequently completed fresh consent and the frozen batch
  ran once per backend. No failed live trial was rerun or tuned away.

Later post-processing worker restarts changed only idle report/resource-cleanup
coordination; they did not restart the active model supervisor or edit its
frozen inputs. Their operator scripts and logs are separate from trial records.
