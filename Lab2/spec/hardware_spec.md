# Hardware Specification: AUP-ZU3 DMA Loopback Design

## 1. Target Platform

| Parameter        | Value                                    |
|------------------|------------------------------------------|
| Board            | Zynq UltraScale+ AUP-ZU3 8GB Development Board |
| FPGA Part        | xczu3eg-sfvc784-2-e (ZynqUS+ MPSoC)     |
| Board Part       | realdigital.org:aup-zu3-8gb:part0:1.0   |
| Vivado Version   | 2025.2                                  |


## 2. Design Requirements

### 2.1 Functional Overview

Create an AXI DMA loopback design for the AUP-ZU3 with a custom AXI-Stream
filter module in the data path. DMA buffers is PS DDR.

- **DMA loopback via DDR**: CPU writes test data into DDR source region →
  DMA MM2S reads from DDR → data passes through a custom RTL filter →
  DMA S2MM writes to DDR destination region → CPU reads and verifies.
- **No external I/O**: No GPIO, no LEDs, no pin constraints. 

### 2.2 Custom RTL Module — `axis_filter`

A simple AXI-Stream passthrough filter with the following interface:

| Port       | Direction | Width | Description                |
|------------|-----------|-------|----------------------------|
| aclk       | input     | 1     | AXI clock                  |
| aresetn    | input     | 1     | Active-low AXI reset       |
| s_axis_tdata  | input  | 32    | Slave data input           |
| s_axis_tkeep  | input  | 4     | Slave byte enables         |
| s_axis_tlast  | input  | 1     | Slave last beat marker     |
| s_axis_tvalid | input  | 1     | Slave valid                |
| s_axis_tready | output | 1     | Slave ready (backpressure) |
| m_axis_tdata  | output | 32    | Master data output         |
| m_axis_tkeep  | output | 4     | Master byte enables        |
| m_axis_tlast  | output | 1     | Master last beat marker    |
| m_axis_tvalid | output | 1     | Master valid               |
| m_axis_tready | input  | 1     | Master ready               |

Initial implementation: wire-through passthrough (all outputs = corresponding
inputs). This module exists at `src/axis_filter.v`.

### 2.3 PS Configuration

| PS Interface       | Direction | Purpose                           |
|--------------------|-----------|-----------------------------------|
| M_AXI_HPM0_FPD     | PS→PL     | Control + data path to PL IPs     |
| S_AXI_HPC0_FPD     | PL→PS     | data path to PS                   |
| pl_ps_irq0         | PL→PS     | Interrupt input                   |
| pl_clk0            | PS→PL     | 100 MHz PL fabric clock           |
| pl_resetn0         | PS→PL     | Active-low reset                  |

All other PS-PL interfaces must be **disabled** (M_AXI_HPM1_FPD, S_AXI_HPC0_FPD, etc.) to avoid validation errors from unconnected clocks.


## 3. PL IP Configuration

### 3.1 AXI DMA (`axi_dma`)

| Parameter                            | Value    | Rationale                    |
|--------------------------------------|----------|------------------------------|
| c_include_sg                         | 0        | Simple mode, no scatter-gather |
| c_sg_length_width                    | 26       | Max transfer                 |
| c_m_axi_mm2s_data_width              | 32       | Match DDR controller width  |
| c_m_axi_s2mm_data_width              | 32       | Match DDR controller width  |
| c_m_axis_mm2s_tdata_width            | 32       | Match axis_filter width     |
| c_s_axis_s2mm_tdata_width            | 32       | Match axis_filter width     |
| c_include_mm2s_dre                   | 1        | Data realignment engine      |
| c_include_s2mm_dre                   | 1        | Data realignment engine      |


### 3.2 Interconnect

| Component            | Configuration              | Purpose                             |
|----------------------|----------------------------|--------------------------------------|
| AXI SmartConnect-0   | 1 SI, 1 MI                 | PS → DMA regs                        |
| AXI SmartConnect-1   | 2 SI, 1 MI                 | DMA_MM2S + DMA_S2MM → PS             |
| Proc Sys Reset       | 1 instance                 | Synchronize pl_resetn0               |

Masters connecting to SmartConnect-0:
- SI[0]: PS M_AXI_HPM0_FPD (CPU access to all peripherals)

Slaves connecting to SmartConnect-0:
- MI[0]: AXI DMA S_AXI_LITE (control registers)

Masters connecting to SmartConnect-1:
- SI[1]: DMA M_AXI_MM2S (reads source data from DDR)
- SI[2]: DMA M_AXI_S2MM (writes result data to DDR)

Slaves connecting to SmartConnect-1:
- SI[0]: PS S_AXI_HPC0_FPD (PL access DDR)


## 4. Address Map

**Network 0** 

Network 0 is in the PL AXI_DMA address space and accessible
by DMA MM2S, and DMA S2MM masters:

| Peripheral       | Base Address  | Size   | Accessed By           |
|------------------|---------------|--------|-----------------------|
| PS S_AXI_HPC0_FPD| 0x0000_0000   | 2 GB   | DMA MM2S + S2MM       |

**Network 1** 

Network 1 is in the PS M_AXI_HPM0_FPD address space and accessible
by CPU:

| Peripheral      | Base Address  | Size   | Accessed By           |
|-----------------|---------------|--------|-----------------------|
| AXI DMA         | 0xA000_0000   | 64 KB  | CPU only              |


## 5. Pin Constraints

**None.** This design has no external I/O pins.


## 6. Clocking

| Clock     | Frequency | Source   | Domain                  |
|-----------|-----------|----------|-------------------------|
| pl_clk0   | 100 MHz   | PS PLL   | All PL logic            |

Single clock domain — no CDC required.

## 7. Data Path

```
    ↓ write test data
CPU → DDR (source region)
    ↓ start DMA
AXI DMA MM2S ← SmartConnect ← DDR (source region)
    ↓ AXI-Stream (32-bit)
axis_filter (passthrough)
    ↓ AXI-Stream (32-bit)
AXI DMA S2MM → SmartConnect → DDR (dest region)
    ↓ read results
CPU ← DDR (dest region)
```


<p class="sphinxhide" align="center"><sub>Copyright © 2026 Advanced Micro Devices, Inc</sub></p>
<p class="sphinxhide" align="center"><sup><a href="https://www.amd.com/en/corporate/copyright">Terms and Conditions</a></sup></p>
