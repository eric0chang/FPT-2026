# HLS rule library — 230 rules (AMD UG1399 v2023.2, tutorial subset)

How to use (details: `reference/kb-guide.md`, Track 2):
1. Pick the topics your design touches from the table below and read only those files (`topics/<file>`); do not read all of them.
2. In a topic file, every `must` / `must-not` row whose condition can occur in your design is a constraint; pick `recipe` / `direction` / `pitfall` rows that fit your structure or current bottleneck.
3. Open `HLS/<ID>.md` for every rule you apply before writing the code (mechanism, conditions, cost, how to check, source page).
4. Anything else: `grep -il <keyword> HLS/*.md` (tags are in each file's front matter).

Types: `must` / `must-not` = requirement (otherwise synthesis error, wrong results, deadlock or an ignored pragma); `recipe` = how to get an effect; `direction` = trade-off or preference with its condition; `pitfall` = symptom -> cause -> fix.

| # | Topic | Rules | File | Covers |
|---|---|---|---|---|
| 2 | Math library | 4 | topics/02-math-library.md | hls_math, math.h/cmath functions, float vs fixed-point math |
| 5 | Dataflow and task-level parallelism | 25 | topics/05-dataflow-and-task-level-parallelism.md | DATAFLOW, PIPO/FIFO channels, STABLE |
| 6 | Streams and FIFOs | 12 | topics/06-streams-and-fifos.md | hls::stream, FIFO depth, blocking/non-blocking access, deadlock |
| 7 | Interfaces and block protocols | 32 | topics/07-interfaces-and-block-protocols.md | axis, ap_fifo/ap_memory/ap_vld ports, ap_ctrl_*, Vivado IP flow |
| 8 | Verification (csim, cosim, testbench) | 11 | topics/08-verification-csim-cosim-testbench.md | test benches, C simulation, C/RTL co-simulation |
| 9 | Loops, pipelining and II | 34 | topics/09-loops-pipelining-and-ii.md | PIPELINE, II, UNROLL, loop-carried dependences, DEPENDENCE, LOOP_FLATTEN/MERGE, trip counts, PERFORMANCE |
| 10 | Arrays and on-chip memory | 13 | topics/10-arrays-and-on-chip-memory.md | ARRAY_PARTITION/RESHAPE, BRAM/URAM/LUTRAM, BIND_STORAGE, memory ports, ROMs, initialization |
| 11 | Data types | 44 | topics/11-data-types.md | ap_int/ap_fixed, bit widths, quantization/overflow, float/double, casts, hls::vector |
| 12 | Functions and hierarchy | 16 | topics/12-functions-and-hierarchy.md | INLINE, top function, templates, classes, recursion, static |
| 13 | Resources, binding and sharing | 11 | topics/13-resources-binding-and-sharing.md | BIND_OP, ALLOCATION, DSP mapping, operator sharing, expression balancing |
| 14 | Unsupported constructs and coding rules | 11 | topics/14-unsupported-constructs-and-coding-rules.md | dynamic memory, pointers, volatile, system calls, __SYNTHESIS__, undefined behaviour |
| 15 | Reports, timing and tool flow | 17 | topics/15-reports-timing-and-tool-flow.md | reading synthesis reports, clock/timing, tool settings, runtime, general design flow |
