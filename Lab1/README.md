# AXI4 Debug Simulation

**Category:** Design Closure
Debug AXI4 protocol violations through AI-guided simulation with Vivado XSim.

## Overview

AXI4 bus protocol violations are notoriously difficult to debug — ordering rules, handshake dependencies, and burst semantics create complex failure modes. This example uses an AI agent to **run Vivado simulations**, analyze assertion failures from the AXI Protocol Checker (PG101), open targeted waveforms, diagnose root causes, and apply minimal RTL fixes — all through natural language.

The included design contains 5 buggy AXI4 master variants, each with a single intentional protocol violation. The AI agent runs each testbench, catches the assertion, shows you the waveform, and waits for your go-ahead before fixing.

> **Note:** This skill requires a **running Vivado MCP server** to launch simulations, open waveforms, and apply fixes interactively.

## What's Included

```
axi4-debug-simulation/
├── scripts/
│   └── create_project.tcl                          # Creates Vivado project with AXI VIP + Protocol Checker
├── rtl/
│   ├── axi_master.sv                               # Correct baseline AXI4 master
│   ├── axi_master_bug1.sv ... axi_master_bug5.sv   # 5 buggy variants
├── tb/
│   ├── tb_axi_master.sv                             # Baseline testbench (correct DUT)
│   ├── tb_axi_master_bug1.sv ... bug5.sv            # Bug testbenches
├── prompts.md                                       # Prompt library (copy-paste examples)
└── .claude/skills/axi4-debug-simulation/            # Bundled agent skill
    └── SKILL.md                                     # Skill instructions
```

## Step-by-Step Instructions

### Step 1 — Create the Vivado project
When you are in vivado environment, (vivado%)

```bash
cd axi4-debug-simulation/
source scripts/create_project.tcl
```

> **Note:** This takes approximately 1–2 minutes. The script creates the project, generates the AXI VIP and Protocol Checker IPs, and configures two simulation filesets.

The script creates a project targeting `xc7a35tcpg236-1` (Artix-7) with two simulation filesets:

| Fileset | Testbenches | Purpose |
|---------|-------------|---------|
| `sim_1` | `tb_axi_master` | Baseline — correct DUT, should pass cleanly |
| `sim_bugs` | `tb_axi_master_bug{1..5}` | 5 buggy variants — each has one protocol violation |

### Step 2 — Verify MCP server is configured

Ensure your MCP configuration is set up.

> **Important:** This example requires a running Vivado MCP server. The agent uses `vivado_start`, `vivado_execute`, and `vivado_stop` MCP tools to launch simulations and open waveforms interactively.

### Step 3 — Run the axi4-debug-simulation skill

**Full debug session:**
```
Open the axi_master_sim project, list the simulation filesets, and run the sim_bugs testbenches to find and fix AXI protocol violations. And screenshot the waveform of all bugs and circule error waveform.
```

**Single bug:**
```
Run tb_axi_master_bug2 from the sim_bugs fileset. Show me the protocol violation and open a waveform.
```

**Baseline verification:**
```
Run sim_1 (the baseline testbench with the correct DUT) to verify it passes cleanly.
```

> **Tip:** See `prompts.md` for a full library of debug prompts.

### Step 4 — What to expect

For each testbench, the agent follows a strict workflow:

1. **Run** — Sets the testbench as top and launches behavioral simulation
2. **Read log** — Extracts the assertion name, failure time, and violated AXI channel
3. **Waveform** — Opens a wave config with color-coded signals for the implicated channel
4. **Diagnose** — Summarizes the violation and presents options: fix it, skip, or add signals
5. **Fix** (on confirmation) — Reads the RTL, identifies the buggy line, and applies a minimal fix
6. **Verify** — Re-runs simulation to confirm the fix, opens a PASS waveform
7. **Repeat** — Moves to the next testbench

> **Human-in-the-Loop:** The skill enforces mandatory pauses after each diagnosis. The agent will NOT read RTL or apply fixes until you explicitly say "fix it".

## AXI4 Protocol Checks

The AXI Protocol Checker (PG101) validates these rules per ARM IHI0022H:

| Channel | Key Assertions | Common Violations |
|---------|---------------|-------------------|
| **AW** (Write Address) | `AWVALID_RESET`, `AWVALID_STABLE` | VALID during reset, unstable signals |
| **W** (Write Data) | `WVALID_RESET`, `WDATA_NUM`, `WLAST` | Wrong beat count, WLAST on incorrect beat |
| **B** (Write Response) | `BVALID_RESET`, `BRESP_WLAST` | Response before last data beat |
| **AR** (Read Address) | `ARVALID_RESET`, `ARVALID_STABLE` | Same as AW channel |
| **R** (Read Data) | `RVALID_RESET`, `RDATA_NUM`, `RLAST` | Wrong beat count, missing RLAST |



## Result Summary
|#|	Testbench | Failure time | Root cause | Fix applied |
|-|-----------|--------------|------------|------------ |
|1|	tb_axi_master_bug1 | 285 ns | WLAST driven on beat 0 instead of the last beat | wlast = (beat_q == cur_len) | 
|2|	tb_axi_master_bug2 | 205 ns | FSM reset into ST_WR_ADDR, so AWVALID was high during reset | reset state ST_WR_ADDR → ST_IDLE | 
|3|	tb_axi_master_bug3 | 285 ns | WDATA driven from the undriven wdata_from_fifo | wdata = cur_beat_wdata | 
|4|	tb_axi_master_bug4 | 535 ns | AWVALID inferred as a latch and never dropped | awvalid_latch = (state_q == ST_WR_ADDR) | 
|5|	tb_axi_master_bug5 | 2235 ns | FSM skipped ST_WR_RESP, so BREADY was never asserted | last beat → ST_WR_RESP | 
<br>
tb_axi_master_bug1

- bug
  <img width="2000" height="787" alt="image" src="https://github.com/user-attachments/assets/a74035a7-ef63-408f-a6f9-2534512cfc23" /> <br>

- fix
  <img width="2000" height="787" alt="image" src="https://github.com/user-attachments/assets/f8c2505a-2aba-4fdb-91c6-2572ea097c7d" /> <br>

<br>
tb_axi_master_bug2

- bug
  <img width="2000" height="547" alt="image" src="https://github.com/user-attachments/assets/011eaa42-12f7-474a-a00e-0ba01bccd24d" /> <br>
 
- fix
  <img width="2000" height="547" alt="image" src="https://github.com/user-attachments/assets/64114436-b2a7-418a-a65e-fb51b3e8531d" /> <br>

<br>
tb_axi_master_bug3

- bug
  <img width="2000" height="787" alt="image" src="https://github.com/user-attachments/assets/eb24a6dd-639f-4c92-a309-05384746388c" /> <br>

- fix
  <img width="2000" height="787" alt="image" src="https://github.com/user-attachments/assets/51ebd9ed-9b1f-45f5-82fd-65cae1ba4b88" /> <br>

<br>
tb_axi_master_bug4

- bug
  <img width="2000" height="847" alt="image" src="https://github.com/user-attachments/assets/4d28fafd-5f15-4c00-b2f8-75ed737e222c" /> <br>

- fix
  <img width="2000" height="847" alt="image" src="https://github.com/user-attachments/assets/5d543ad9-4b9f-44ae-bd07-33a69dfd66b1" /> <br>

<br>
tb_axi_master_bug5

- bug
  <img width="2000" height="787" alt="image" src="https://github.com/user-attachments/assets/690bdb85-1129-42e0-8fa6-a42b6c65b24f" /> <br>

- fix
  <img width="2000" height="787" alt="image" src="https://github.com/user-attachments/assets/f83b9684-0c21-437f-88dc-4240104e7249" /> <br>


## What You'll Learn

- How **natural language prompts** drive a full simulation debug workflow — the agent runs XSim, reads assertion logs, opens waveforms, and applies RTL fixes
- How the AXI Protocol Checker (PG101) validates ARM IHI0022H rules at simulation time
- How to interpret common AXI4 assertion failures
- How the skill enforces **human-in-the-loop** confirmation — the agent diagnoses but waits for your approval before touching RTL
- How to use the AXI VIP slave memory model (PG267) for burst write/read verification

<p class="sphinxhide" align="center"><sub>Copyright © 2026 Advanced Micro Devices, Inc</sub></p>
<p class="sphinxhide" align="center"><sup><a href="https://www.amd.com/en/corporate/copyright">Terms and Conditions</a></sup></p>
