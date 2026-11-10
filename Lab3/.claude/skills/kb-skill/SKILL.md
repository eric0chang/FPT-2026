---
name: kb-skill
description: HLS Knowledge Base (recording build: the final design is written back) — before writing Vitis HLS C++, look up similar past designs in the KB API (Track 1) and the HLS rule library rules/index.md -> rules/topics/*.md -> rules/HLS/*.md (Track 2). Manual invocation only (/kb-skill).
disable-model-invocation: true
---

# kb-skill — HLS Knowledge Base (recording build: writes the final design back)

This SKILL.md is only an entry point. The procedure lives in `reference/kb-guide.md` next to this file: **Read it before writing any HLS code**, then follow it.

## Narrate the KB in the chat (required)

The user watches the chat, not the tool calls. At these five points write chat text, with these headings:

1. Before Track 1: `**KB Track 1** — searching past <type> designs in the KB...`
2. After Track 1: `**KB Track 1 result**`, a table | Design | Part | Latency | Resources | What I reuse / what I change |, then one line: which design I follow and why. Compare its resources and latency with the spec limits, and say what I change to meet them.
3. Before Track 2: `**KB Track 2** — topics I picked: <number and name of each>`
4. After Track 2, before writing any HLS code: `**KB Track 2 result**`, a table | Rule | What it says (one line) | Where in my code | (only rules whose file you opened). Write it before running anything else (tool checks, Python, file writes). Keep it to the 5–10 rules that matter most.
5. After the IP export: `**KB write-back**` — project name, iteration number and `iteration_id` returned by the API (guide, "Write-back").

Later, when a step follows a rule, name it (e.g. "pipelining the MAC loop, HLS-1032").

## Files

- `reference/kb-guide.md` — KB API (Track 1), rule lookup (Track 2), how to cite rules
- `rules/index.md` — topic table (13 topics); `rules/topics/<file>` — one row per rule; `rules/HLS/<ID>.md` / `rules/EXP/<ID>.md` — full rule

## Bottom line (keep even without reading the guide)

- Do both tracks before writing code: Track 1 (similar designs from the KB API), then Track 2 (rule library).
- Read with the `GET` endpoints in the guide. Write exactly once: one `POST /api/design/complete_iteration` for the final design after the IP export (guide, "Write-back"). No other `POST` / `PUT` / `DELETE`.
- Rules come only from `rules/`: `HLS-####` from AMD UG1399 v2023.2, and `EXP-###` lessons from past designs (topic 16, always read it). Cite them by ID; do not cite `R###` / `P###` codes.
- The task specification takes precedence over a rule or a past design when they conflict (e.g. interface, target part, data types).
- Do not fabricate API results or rule content. If the API is unreachable or returns nothing, say so and continue with Track 2.
