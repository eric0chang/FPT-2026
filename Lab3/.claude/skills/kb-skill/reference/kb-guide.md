# HLS Knowledge Base — lookup guide (recording build: reads, plus one write-back)

The Knowledge Base has two parts that complement each other:

|              | Track 1: past designs                                   | Track 2: rule library                                        |
|--------------|---------------------------------------------------------|--------------------------------------------------------------|
| What         | Recorded iterations of similar designs: approach, pragmas, latency, resources, code | Rules from AMD UG1399 v2023.2 that constrain or improve this design |
| Where        | KB API `GET /api/design/similar`                        | `rules/` in this skill folder                                |
| Gives        | What actually worked on a similar design                | Which constraints and techniques hold in general            |
| Order        | First                                                   | Second (uses Track 1 results to pick topics)                 |

Paths below are relative to this skill folder (`.claude/skills/kb-skill/` under the working directory).


## Track 1: past designs (KB API, GET only)

```bash
KB=${KB_API:-http://localhost:8003}                     # recording KB (writable copy)
curl -s "$KB/health"                                    # reachable?
```

| Endpoint | Returns |
|----------|---------|
| `GET /api/design/similar?project_type=<type>&limit=<n>` | Best recorded iterations of that type, sorted by `ii_achieved` ascending (`limit` default 5, max 20). Fields: `project_name`, `iteration_id`, `iteration_number`, `approach_description`, `pragmas_used`, `cursor_reasoning`, `user_specification`, `ii_achieved`, `latency_cycles`, `resource_usage` (JSON string), `created_at` |
| `GET /api/design/<iteration_id>/code` | One iteration in full, adds `code_snapshot` (all source files) and `user_reference_code` |
| `GET /api/projects?type=<type>` | Project list (names, types) |

Unknown `project_type` returns `200` with `results: []`. Types in use: `cnn`, `attention`, `mlp`, `ssm`, `moe`, `stencil`, `hyperconn`.

**Steps**

0. Write in the chat: `**KB Track 1** — searching past <type> designs in the KB...`
1. Query the design's type, e.g. `curl -s "$KB/api/design/similar?project_type=cnn&limit=10" | jq '.results[] | {project_name, iteration_id, latency_cycles, resource_usage, approach_description, pragmas_used}'`.
2. Pick the 1–3 entries closest to the task (same kind of model, same interface, same target). Read `approach_description`, `pragmas_used`, `cursor_reasoning`; parse `resource_usage` with `jq 'fromjson'`.
3. For the closest entry, fetch the code: `curl -s "$KB/api/design/<iteration_id>/code" | jq -r '.code_snapshot'`. If it matches the task's interface and model, start from this code: copy its functions and loop structure, then change only what the task specification defines differently (data types, lanes to meet the resource limits, part, clock) — EXP-000. Do not rewrite its structure from scratch.
4. Note what you took: project name, iteration, and the techniques reused. Use `pragmas_used` to pick topics in Track 2.
5. Write in the chat: `**KB Track 1 result**`, a table | Design | Part | Latency | Resources | What I reuse / what I change | (1–3 rows, or "none relevant"), then one line: which design you follow and why. Compare its resources and latency with the spec limits, and say what you change to meet them.

Older entries may cite retired `R###` / `P###` codes. Read them as plain text; cite the matching `HLS-####` rule instead.


## Track 2: rule library (local files)

230 UG1399 rules in 12 topics, plus topic 16 (2 `EXP-###` lessons from past designs, always read it) — a subset of the full library, chosen for single-kernel AXI-Stream IP in the Vivado IP flow. Rule types: `must` / `must-not` (otherwise synthesis error, wrong results, deadlock or an ignored pragma), `recipe` (how to get an effect), `direction` (trade-off with its condition), `pitfall` (symptom -> cause -> fix).

**Step 1: Pick topics.** Read `rules/index.md` (topic table only, about 25 lines). From the task specification and the Track 1 results, list the topics this design touches — usually several. Example: an AXI-Stream CNN accelerator touches *Interfaces and block protocols*, *Streams and FIFOs*, *Loops, pipelining and II*, *Arrays and on-chip memory*, *Data types*, *Verification*, plus *Dataflow* if it is split into tasks, and always *16 Lessons from past designs*. Then write in the chat: `**KB Track 2** — topics I picked: <number and name of each>`.

**Step 2: Read those topic files.** Read only `rules/topics/<file>` of the topics you picked. In each file:
- every `must` / `must-not` row whose condition can occur in this design is a constraint (these rows come first);
- `recipe` / `direction` / `pitfall` rows that fit the planned structure are candidates.

**Step 3: Open the rule files.** For every candidate you apply, and every constraint you are unsure about, read `rules/HLS/<ID>.md` (or `rules/EXP/<ID>.md`): mechanism, exact conditions, cost, how to check the effect (report line or warning), UG1399 page.

**Step 4: Report, before writing any HLS code.** Write in the chat: `**KB Track 2 result**`, a table | Rule | What it says (one line) | Where in my code | — only rules whose file you opened. Write it before running anything else (tool checks, Python, file writes). Keep it to the 5–10 rules that matter most.

**Step 5: Search when a topic does not cover the problem** (e.g. a new csynth warning):

```bash
R=.claude/skills/kb-skill/rules
grep -il "dependence" $R/HLS/*.md        # II limited by a carried dependence
grep -il "200-656\|deadlock" $R/HLS/*.md # deadlock warning in the csynth log
```

**Selection order**
1. Constraints first — every `must` / `must-not` whose condition can occur in the design.
2. Fit — `recipe` / `direction` / `pitfall` rows that address the current structure or the bottleneck in the csynth report.
3. Cost — a `direction` rule states its cost; weigh it against the task limits (resources, latency) before applying it.

Keep the set focused: a few rules that match the design beat a long list. Your own analysis of the csynth report is as valid as the library; use the rules to avoid violating a `must` / `must-not` and to find techniques you would not otherwise try. If a rule says the manual contradicts itself on a point, follow the safe action it states.

## Write-back (once, after the IP export)

Record the final design so the next run finds it in Track 1. Only after csim, the final csynth and cosim pass and the IP is exported; never record a failed or intermediate design.

1. project_id: `curl -s "$KB/api/projects?type=cnn&limit=200" | jq -r '.results[] | select(.name=="LeNet_HardSwish_Fixed_AXIS_AUPZU3") | .id'`. Empty: generate one (`python3 -c 'import uuid; print(uuid.uuid4())'`); the API then creates the project.
2. Build `hls/tmp/kb_record.json` with Python (`json.dump`, so the code is escaped correctly), numbers from the final csynth report:
   ```json
   {"project_id": "<id>", "project_name": "LeNet_HardSwish_Fixed_AXIS_AUPZU3", "project_type": "cnn",
    "target_device": "xczu3eg-sfvc784-2-e",
    "iteration": {"project_id": "<same id>", "approach_description": "<2-3 sentences: structure, data types, lanes>",
                  "code_snapshot": "<lenet.h + lenet.cpp + run_hls.tcl, each preceded by // ===== <file> =====>",
                  "pragmas_used": ["<one string per pragma kind>"],
                  "cursor_reasoning": "<Track 1 design followed, what changed and why>",
                  "user_specification": "<spec limits in one line>"},
    "synthesis_result": {"ii_achieved": <top interval>, "ii_target": <top interval>, "latency_cycles": <csynth latency>,
                         "timing_met": true, "clock_period_ns": 10.0,
                         "resource_usage": {"LUT": 0, "FF": 0, "DSP": 0, "BRAM": 0}},
    "rules_applied": [{"rule_code": "HLS-####", "previous_ii": 1, "current_ii": 1, "success": true}]}
   ```
3. `curl -s -X POST "$KB/api/design/complete_iteration" -H 'Content-Type: application/json' -d @hls/tmp/kb_record.json`
4. Write in the chat: `**KB write-back**` — project name, `iteration_number`, `iteration_id` from the response. If the call fails, show the error and continue; do not retry with other endpoints.


## Citing rules

- In the source, put the rule ID next to the pragma or construct it justifies:
  ```cpp
  #pragma HLS PIPELINE II=1   // HLS-1032: pipeline the inner MAC loop
  ```
- In the task's report, list per design:
  ```
  Track 1: <project_name> iteration <n> — <what was reused>
  Topics read: <topic numbers>
  Rules applied: HLS-#### - <what changed because of it>        (one line each)
  Rules considered, not applied: HLS-#### - <why not>
  ```
  List only rules whose file you actually opened.
