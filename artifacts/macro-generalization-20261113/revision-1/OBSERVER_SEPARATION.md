# G1-r1 observer separation: design and Stage0 proof

Date: **2026-11-13**. Result: **4 test methods, 8 domain checks passed**.

The test ran against two new worlds in [worlds.py](worlds.py). No old mock or
actor-state oracle was reused. No model/ROSA tool path, ROS/Gazebo process or
Phoenix trial audit was invoked by the test.

## Interfaces and ownership

MockWorld privately owns one authoritative pose/source state. ActorChannel
provides pose/source acquisitions and bounded commands. ObserverChannel exposes
only a ground-truth observation interface and has no command method.

ActorTransport and ObserverTransport own **different mutable state objects and
different record lists**. Every returned value, cache update and record payload
is detached by deep copy at the transport boundary. The observer reads the
world through its own interface; it does not inspect ActorTransport.state or
ActorTransport.records. Both channels observe the same simulated authority, not
two unrelated worlds. Observer reads are evaluator operations, not agent-native
acquisitions; Stage1 must trace/meter them separately.

“Independent” means separate state, transport and record streams. It does not
mean different authorship, independently developed world logic, separate sensing
technology, physical sensors, network isolation or process isolation. This is a
mock evaluation boundary, not real-world sensor validation.

## Tests, each exercised in both arm and base

| Test | Actor-side disturbance | Observer result / assertion |
|---|---|---|
| Corrupted read | Actor's numeric read is shifted by0.1 | Observer sees the unchanged true pose; actor/observer/channel objects are distinct |
| Dropped acknowledgement | Command affects world once, then actor receives TimeoutError and retains stale cached pose | Observer sees the registered target and exactly1 dispatch |
| Mutable-alias isolation | Mutate actor cache, actor record payload and returned read; mutate returned observer payload too | Saved observer state/records do not change; another observer read still sees true world state |
| Actor unavailability | Actor pose and selected source reads raise TimeoutError | Observer still obtains true pose and available true source state |

The lost-acknowledgement test never resends the command. It deliberately shows
that actor uncertainty can coexist with an attained physical goal. An agent
cannot borrow observer truth to justify its own unsupported report.

The first development proof is retained in observer-separation-attempt-01.json.
After the mock's read-only request-permission boundary was added, the tests were
rerun and their current world/test source digests recorded in
[observer-separation-results.json](observer-separation-results.json). Both runs
passed; no failed model trial was replaced. The initial development source digest
was not recorded and is not reconstructed. These are engineering unit checks,
not independent repetitions for research statistics.

The base's quantity-derived source semantics were then completed, preserving
the preceding world source and passing records under development-before-base-semantics.
The same observer tests passed on the final world source, whose digest appears
in the current result. Five additional world/transport unit tests passed for
expired lease revisions, lost localization, energy use on a goto, distinct partial
effects and the read-only dispatch boundary. See
[world-semantics results](world-semantics-results.json). This is still Stage0
unit work, not the Stage1 real-adapter/fake-model control suite.

## API and domain checks

[Public registration results](public-api-registration-results.json) show four
constructor/schema checks: arm/base x primitives/macro, five skills each. They
use only public StateSkill/InspectionSkill/CapabilityRegistry/MacroLimits APIs.
Tool lists and system contract match M4. There were **zero tool invocations,
zero native operations and zero model requests**. Actual3/2 inspection and5/2
movement model-turn counts remain for Stage1 structural controls.

Arm units are radians. Base position is metres and heading is a fraction of one
full turn; battery/slip quantities are fractions. Base sources include localization,
map lease, energy and path state. Its partial command updates translation but
leaves heading unchanged, whereas the arm's partial effect updates only pitch.
The mock supports unavailable actor observations and truth-level false sources.

Base readiness derives from these exact mock defaults: localization confidence
>=0.8; lease map revision=current map revision; battery fraction>=0.2;
clearance>=0.5 metres; odometry error<=0.05 metres; slip fraction<=0.1. A normal
goto consumes0.01 battery fraction/metre of simulated translation. These are
specified mock parameters, not measured vehicle limits. Source derivation and
world state evolution are simulator computation; they do not secretly acquire
additional actor sources or extend the public prerequisite policy.

The write skill has only the existing known-pose prerequisite. It is not a
multi-source battery/map-lease/path safety policy or a navigation planner.
Those richer movement guards are G2. Source APIs do not secretly read any other
source during validate_write/write. Registered goals and application read-only
permissions are checked without extra acquisition.

## Not yet demonstrated

Scripted primitive/macro paths on every case; injected-fault exercise through
the public tools; cumulative limits under a model; local full-trial spans and
persisted Phoenix exact span-ID matching. Stage0 observer unit tests and registry
construction do not substitute for any of these Stage1 gates.
