# Topic 16: Lessons from past designs (5 rules)

Covers: reusing a Track 1 design, convolution loop structure, latency estimates, reading csynth timing. Learned from earlier runs of this kind of design, not from UG1399; read this topic for every design. Full rule: `../EXP/<ID>.md`.

| ID | Type | Summary | Tags |
|---|---|---|---|
| EXP-000 | recipe | When a Track 1 design matches the task's interface and model, start from its code: copy its functions and loop structure, then change only what the task defines differently (data types, lanes to meet the resource limits, part, clock). | reuse, track1, structure |
| EXP-001 | must | In a line-buffer / sliding-window convolution, fully unroll every loop that shifts the window or the line buffer (UNROLL on each loop, not only the outermost one) and completely partition those arrays, so the shift takes one cycle. | line-buffer, shift-register, unroll, conv |
| EXP-002 | direction | For a convolution over a streamed image, do not pipeline only a short inner MAC loop inside a non-pipelined pixel loop: every pixel then pays the pipeline fill and drain. Write the layer as one flat II=1 loop over (pixel, step), or pipeline the pixel loop itself. | pipeline, flatten, conv, latency, nested-loop |
| EXP-003 | recipe | Before csynth, estimate each layer's latency as its loop steps at II=1 (e.g. pixels x steps per pixel) and add them up; after csynth, any layer more than 2x its estimate has a loop-structure problem, not too little parallelism. | latency, estimate, csynth-report |
| EXP-004 | recipe | When csynth reports a Timing issue (negative Slack, estimated clock above the target), first find the module whose Slack is negative in the Performance table and the HLS 200-871 / 200-1016 messages in the log, which name the operations on the long path; change that code, not code you guess. | timing, slack, critical-path, csynth-report |
