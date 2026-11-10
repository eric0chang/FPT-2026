# Topic 16: Lessons from past designs (2 rules)

Covers: reusing a Track 1 design, float accumulation. Learned from earlier runs of this kind of design, not from UG1399; read this topic for every design. Full rule: `../EXP/<ID>.md`.

| ID | Type | Summary | Tags |
|---|---|---|---|
| EXP-000 | recipe | When a Track 1 design matches the task's interface and model, start from its code and its run_hls.tcl: copy its functions, loop structure, buffer shapes, pragmas and tool config lines, then change only what the task defines differently (data types, lanes to meet the resource limits, part, clock). Before the first csynth, check that nothing else was dropped or changed. | reuse, track1, structure |
| EXP-001 | must | Do not accumulate in float inside a loop (e.g. the softmax sum of exponentials): sum in ap_fixed / ap_ufixed (e.g. ap_ufixed<32,4> for ten values in [0,1]) and convert to float once, if at all. | float, accumulator, timing, softmax |
