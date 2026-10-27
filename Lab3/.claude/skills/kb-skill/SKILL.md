---
name: kb-skill
description: HLS Knowledge Base (read-only) — before writing Vitis HLS C++, look up similar past designs in the KB API (Track 1) and the HLS rule library rules/index.md -> rules/topics/*.md -> rules/HLS/*.md (Track 2). Manual invocation only (/kb-skill).
disable-model-invocation: true
---

# kb-skill — HLS Knowledge Base (read-only)

This SKILL.md is only an entry point. The procedure lives in `reference/kb-guide.md` next to this file: **Read it before writing any HLS code**, then follow it.

## Files

- `reference/kb-guide.md` — KB API (Track 1), rule lookup (Track 2), how to cite rules
- `rules/index.md` — topic table (12 topics); `rules/topics/<file>` — one row per rule; `rules/HLS/<ID>.md` — full rule

## Bottom line (keep even without reading the guide)

- Do both tracks before writing code: Track 1 (similar designs from the KB API), then Track 2 (rule library).
- The KB is **read-only**: use only the `GET` endpoints listed in the guide. Never send `POST` / `PUT` / `DELETE`, and do not try to record iterations.
- Rules come only from `rules/` (IDs `HLS-####`, from AMD UG1399 v2023.2). Cite them by ID; do not cite `R###` / `P###` codes.
- The task specification takes precedence over a rule or a past design when they conflict (e.g. interface, target part, data types).
- Do not fabricate API results or rule content. If the API is unreachable or returns nothing, say so and continue with Track 2.
