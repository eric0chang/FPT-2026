# Hardware Specification: AUP-ZU3 LeNet Inference Design

## 1. Target Platform

| Parameter        | Value                                    |
|------------------|------------------------------------------|
| Board            | Zynq UltraScale+ AUP-ZU3 8GB Development Board |
| FPGA Part        | xczu3eg-sfvc784-2-e (ZynqUS+ MPSoC)     |
| Board Part       | realdigital.org:aup-zu3-8gb:part0:1.0   |
| Vivado Version   | 2025.2                                  |

Use the same Vivado version as the Vitis HLS that exported the IP (2025.2). Drive
Vivado through the Vivado MCP server.

Paths in this spec are relative to the `Lab3/` folder; pass them to Vivado as absolute
paths (the Vivado session does not start in `Lab3/`).


## 0. Build Strategy: reuse the Lab2 project

Lab2 already built and verified this platform. Start from its project and swap one
block; §2–§7 describe the resulting design.

1. **Find** the Lab2 project: `../Lab2/vivado/*.xpr`, otherwise any `*.xpr` under `../Lab2/`
   whose block design `design_1` contains the `axis_filter` module reference.
2. **Copy** it: `open_project` the Lab2 `.xpr`, then
   `save_project_as aup_zu3_lenet <Lab3>/vivado -force`. All further changes go to the copy;
   never modify or re-run the Lab2 project.
3. **Swap** in `design_1`:
   - delete the `axis_filter` cell and remove `axis_filter.v` from the project sources;
   - add the HLS IP repository (§3.2) and instantiate `lenet_axis_0`;
   - connect DMA `M_AXIS_MM2S` → `lenet_axis_0/s_axis`, `lenet_axis_0/m_axis` → DMA
     `S_AXIS_S2MM`, `ap_clk` to the clock of the DMA stream ports (`pl_clk0`), `ap_rst_n`
     to the reset that drives the DMA `axi_resetn` (`peripheral_aresetn`).
   Keep everything else from Lab2 as it is (PS configuration, DMA, SmartConnects, address
   map, instance names). The instance names in §3 apply to a rebuild only; a reused
   project keeps the names Lab2 gave (e.g. the reset block may be `rst_ps8_0_100M`).
   Only the DMA name is required: check that it is `axi_dma_0` (the notebook uses it)
   and that its stream width is 32 bits.
4. **Build**: `validate_bd_design`, save, regenerate the HDL wrapper, reset and run synthesis
   and implementation through `write_bitstream`, then write the reports and copy the
   outputs (§8).

**Fallback:** if no Lab2 project is found, or it does not open or validate, build the
design from scratch in `<Lab3>/vivado/aup_zu3_lenet` as specified in §2–§7.


## 2. Design Requirements

### 2.1 Functional Overview

Same platform as Lab2 (AXI DMA loopback via DDR). When the Lab2 project is reused (§0),
its PS and interconnect settings stand, even where they differ from §2.3–§4. The only change is the stream
processing block: the `axis_filter` passthrough is replaced by the HLS IP
`lenet_axis`, which classifies one 28×28 MNIST image per transfer.

- **Inference via DDR**: CPU writes one image (784 × float32) into the DDR source
  region → DMA MM2S reads it → `lenet_axis` computes 10 class probabilities →
  DMA S2MM writes them (10 × float32) to the DDR destination region → CPU reads them.
- **No external I/O**: No GPIO, no LEDs, no pin constraints.

### 2.2 HLS IP — `lenet_axis`

Exported by Vitis HLS (see `spec/hls_spec.md`).

| Item          | Value                                         |
|---------------|-----------------------------------------------|
| IP repository | `hls/lenet_prj/solution1/impl/ip`             |
| VLNV          | `xilinx.com:hls:lenet_axis:1.0`               |
| Instance name | `lenet_axis_0`                                |
| Control       | `ap_ctrl_none` — free-running, no AXI-Lite, no address |

| Port            | Direction | Width | Description                        |
|-----------------|-----------|-------|------------------------------------|
| ap_clk          | input     | 1     | Clock                              |
| ap_rst_n        | input     | 1     | Active-low reset                   |
| s_axis_TDATA    | input     | 32    | Pixel (float32), 784 words / image |
| s_axis_TKEEP    | input     | 4     | Byte enables                       |
| s_axis_TSTRB    | input     | 4     | Byte strobes                       |
| s_axis_TLAST    | input     | 1     | Last beat marker (ignored)         |
| s_axis_TVALID   | input     | 1     | Valid                              |
| s_axis_TREADY   | output    | 1     | Ready (backpressure)               |
| m_axis_TDATA    | output    | 32    | Probability (float32), 10 words / image |
| m_axis_TKEEP    | output    | 4     | Byte enables                       |
| m_axis_TSTRB    | output    | 4     | Byte strobes                       |
| m_axis_TLAST    | output    | 1     | High on the 10th word              |
| m_axis_TVALID   | output    | 1     | Valid                              |
| m_axis_TREADY   | input     | 1     | Ready                              |

Connect `s_axis` / `m_axis` as AXI-Stream **interfaces** (not individual pins).

### 2.3 PS Configuration

Instantiate the PS as `zynq_ultra_ps_e_0` and **apply the board preset first**
(`apply_bd_automation -rule xilinx.com:bd_rule:zynq_ultra_ps_e -config {apply_board_preset "1"}`);
DDR and MIO settings come from the preset. Then set the PS-PL interfaces below.
Note: the AUP-ZU3 preset enables M_AXI_HPM0_LPD and disables M_AXI_HPM0_FPD, so both
must be changed explicitly.

| PS Interface       | Direction | Purpose                     | CONFIG parameter                         | Value |
|--------------------|-----------|-----------------------------|------------------------------------------|-------|
| M_AXI_HPM0_FPD     | PS→PL     | Control path to PL IPs      | `PSU__USE__M_AXI_GP0`                    | 1     |
| S_AXI_HPC0_FPD     | PL→PS     | Data path to PS DDR         | `PSU__USE__S_AXI_GP0`                    | 1     |
| pl_ps_irq0         | PL→PS     | Interrupt input             | `PSU__USE__IRQ0`                         | 1     |
| pl_clk0            | PS→PL     | 100 MHz PL fabric clock     | `PSU__FPGA_PL0_ENABLE`, `PSU__CRL_APB__PL0_REF_CTRL__FREQMHZ` | 1, 100 |
| pl_resetn0         | PS→PL     | Active-low reset            | (enabled with pl_clk0)                   | —     |

All other PS-PL interfaces must be **disabled** to avoid validation errors from
unconnected clocks: M_AXI_HPM1_FPD (`PSU__USE__M_AXI_GP1`), M_AXI_HPM0_LPD
(`PSU__USE__M_AXI_GP2`), S_AXI_HPC1/HP0~3/LPD (`PSU__USE__S_AXI_GP1`…`GP6`), ACP, ACE.

S_AXI_HPC0_FPD keeps its default 128-bit width and is used as a **non-coherent** port
(PYNQ flushes/invalidates the DMA buffers). The BD 41-237 AxUSER width warning between
SmartConnect-1 and S_AXI_HPC0_FPD is expected and benign.


## 3. PL IP Configuration

### 3.1 AXI DMA (`axi_dma`, instance `axi_dma_0` — the PYNQ notebook uses this name)

| Parameter                            | Value    | Rationale                    |
|--------------------------------------|----------|------------------------------|
| c_include_sg                         | 0        | Simple mode, no scatter-gather |
| c_sg_length_width                    | 26       | Max transfer                 |
| c_m_axi_mm2s_data_width              | 32       | Match stream width; SmartConnect-1 converts to the 128-bit HPC0 port |
| c_m_axi_s2mm_data_width              | 32       | Match stream width; SmartConnect-1 converts to the 128-bit HPC0 port |
| c_m_axis_mm2s_tdata_width            | 32       | Match lenet_axis width      |
| c_s_axis_s2mm_tdata_width            | 32       | Match lenet_axis width      |
| c_include_mm2s_dre                   | 1        | Data realignment engine      |
| c_include_s2mm_dre                   | 1        | Data realignment engine      |

`c_addr_width` stays at its default (32); only the low 2 GB DDR segment is mapped (§4).

### 3.2 HLS IP (`lenet_axis`)

No parameters. Add `hls/lenet_prj/solution1/impl/ip` to the project's
`ip_repo_paths`, run `update_ip_catalog`, then instantiate `xilinx.com:hls:lenet_axis:1.0`.

### 3.3 Interconnect

| Component            | Instance           | Configuration              | Purpose                             |
|----------------------|--------------------|----------------------------|--------------------------------------|
| AXI SmartConnect-0   | `smartconnect_0`   | 1 SI, 1 MI                 | PS → DMA regs                        |
| AXI SmartConnect-1   | `smartconnect_1`   | 2 SI, 1 MI                 | DMA_MM2S + DMA_S2MM → PS             |
| Proc Sys Reset       | `proc_sys_reset_0` (Lab2 project: keep its name, e.g. `rst_ps8_0_100M`) | 1 instance | Synchronize pl_resetn0; `peripheral_aresetn` drives DMA `axi_resetn`, both SmartConnects `aresetn` and `lenet_axis_0/ap_rst_n` |
| Concat               | `xlconcat_0`       | 2 ports                    | In0 = DMA `mm2s_introut`, In1 = DMA `s2mm_introut` → `pl_ps_irq0` |

Masters connecting to SmartConnect-0:
- SI[0]: PS M_AXI_HPM0_FPD (CPU access to all peripherals)

Slaves connecting to SmartConnect-0:
- MI[0]: AXI DMA S_AXI_LITE (control registers)

Masters connecting to SmartConnect-1:
- SI[0]: DMA M_AXI_MM2S (reads image from DDR)
- SI[1]: DMA M_AXI_S2MM (writes probabilities to DDR)

Slaves connecting to SmartConnect-1:
- MI[0]: PS S_AXI_HPC0_FPD (PL access DDR)

Stream connections:
- DMA M_AXIS_MM2S → `lenet_axis_0/s_axis`
- `lenet_axis_0/m_axis` → DMA S_AXIS_S2MM

Interrupts: DMA `mm2s_introut` and `s2mm_introut` → `xlconcat_0` → PS `pl_ps_irq0`.


## 4. Address Map

**Network 0**

Network 0 is in the PL AXI_DMA address space and accessible
by DMA MM2S, and DMA S2MM masters:

| Peripheral       | Base Address  | Size   | Accessed By           |
|------------------|---------------|--------|-----------------------|
| PS S_AXI_HPC0_FPD| 0x0000_0000   | 2 GB   | DMA MM2S + S2MM       |

Map segment `HPC0_DDR_LOW` for both DMA masters. Exclude `HPC0_LPS_OCM` and
`HPC0_DDR_HIGH` (`exclude_bd_addr_seg`).

**Network 1**

Network 1 is in the PS M_AXI_HPM0_FPD address space and accessible
by CPU:

| Peripheral      | Base Address  | Size   | Accessed By           |
|-----------------|---------------|--------|-----------------------|
| AXI DMA         | 0xA000_0000   | 64 KB  | CPU only              |

`lenet_axis` has no AXI-Lite interface and no address.


## 5. Pin Constraints

**None.** This design has no external I/O pins.


## 6. Clocking

| Clock     | Frequency | Source   | Domain                  |
|-----------|-----------|----------|-------------------------|
| pl_clk0   | 100 MHz   | PS PLL   | All PL logic (incl. `lenet_axis_0/ap_clk`) and the PS AXI port clocks `maxihpm0_fpd_aclk`, `saxihpc0_fpd_aclk` |

Single clock domain — no CDC required. Timing must close: post-route WNS ≥ 0, WHS ≥ 0.


## 7. Data Path

```
    ↓ write 784 × float32 (one image)
CPU → DDR (source region)
    ↓ start DMA
AXI DMA MM2S ← SmartConnect ← DDR (source region)
    ↓ AXI-Stream (32-bit, 784 beats)
lenet_axis (HLS IP: conv → HardSwish → pool → conv → pool → fc → fc → softmax)
    ↓ AXI-Stream (32-bit, 10 beats, TLAST on the 10th)
AXI DMA S2MM → SmartConnect → DDR (dest region)
    ↓ read 10 × float32 probabilities
CPU ← DDR (dest region)
```


## 8. Build Outputs

| Item               | Path                                           |
|--------------------|------------------------------------------------|
| Vivado project     | `vivado/aup_zu3_lenet.xpr`, block design `design_1`, top `design_1_wrapper` |
| Bitstream for PYNQ | `pynq/lenet.bit` ← copy of `vivado/aup_zu3_lenet.runs/impl_1/design_1_wrapper.bit` |
| Hardware handoff   | `pynq/lenet.hwh` ← copy of `vivado/aup_zu3_lenet.gen/sources_1/bd/design_1/hw_handoff/design_1.hwh` |
| Reports            | `vivado/timing_summary.rpt`, `vivado/utilization.rpt` (flat), `vivado/utilization_hier.rpt` (`-hierarchical`, for `lenet_axis_0` alone) |

No `.xsa` is needed. Never place one next to `pynq/lenet.bit`: PYNQ would try to parse it instead of the `.hwh`.
