# Pre-inference amendment: classify bounded browser UI rendering

Date: **2026-11-13**. Recorded with **zero Phase 1 model requests or outputs**.
The owner confirmed apps paused and instructed recheck/run. Original freeze,
protocol and nine frozen files are retained under
`pre-inference-amendment-01/original/` with their original manifest.

The original gate classified Chrome's ordinary 3D window rendering above 2% as
external GPU work, although equivalent desktop rendering from Code/dwm was
allowed. Fresh DXGI enumeration maps NVIDIA to
`0x00000000_0x092439e5`, Intel to `0x00000000_0x000103ac` for this boot; current
counter samples retain adapter identifiers. Chrome did have a small NVIDIA 3D
reading, so this is not falsely described as only integrated-GPU activity.

Fresh samples show total NVIDIA utilization 2%, 2%, 2%. After settling, Chrome
3D samples are about 2.5-3%; the later inventory has no video-decode sample above
1%. Owner paused the relevant apps. These measurements motivate correcting the
display classification, not selecting a model condition after observing output.

The sole gate change is to allow **Chrome 3D rendering <=5%** as bounded desktop
UI work. Browser video-decode >2%, browser non-3D/compute work >2%, browser 3D >5%,
other non-display processes >2%, and pre-request NVIDIA total >10% remain stops.
Code/dwm/OS display exceptions, monitoring and all other stop rules are unchanged.
This is not a dedicated idle machine, and residual desktop/CPU/memory/thermal
noise remains a limitation. No claim that this proves absence of every source of
interference is made. Later output cannot justify changing these rules.

No change to fixtures, tool contracts, weights, profiles, model options, order,
warm-up/repeats, 1.5x speed gate, 9/10 agreement, truncation gate, deadlines or
45-request maximum (30 A/B plus conditional 15 C). No inference retry or budget
reset. No application is closed. Original preflight failures remain in the record.

This amendment supersedes only the original protocol's browser-UI classification.
The new freeze must be recorded and verified before launch.
