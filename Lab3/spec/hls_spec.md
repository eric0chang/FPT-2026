# HLS Specification: Custom LeNet → AXI-Stream IP

## 1. Goal

Convert the Keras model `model/custom_lenet_model.h5` into a **Vitis HLS IP written
from scratch in C++**. The IP replaces the
`axis_filter` passthrough of Lab2: the DMA streams one image in, the IP streams the
10 class probabilities out.


## 2. Target Platform & Tools

| Parameter        | Value                                                      |
|------------------|------------------------------------------------------------|
| FPGA Part        | xczu3eg-sfvc784-2-e (AUP-ZU3)                              |
| Clock            | 10 ns (100 MHz, driven by PS `pl_clk0`)                    |
| Vitis HLS        | 2025.2                                                     |
| Python           | TensorFlow 2.x (only for reading the `.h5`)                |

Past designs in the Knowledge Base may target other parts (e.g. `xcu250-figd2104-2L-e`);
use this part and clock in `set_part` / `create_clock`.


## 3. Model Definition

### 3.1 Layers

Source of truth: `model/custom_lenet_model.h5` (load it after `import custom_layers`
from `model/`). Layout is `channels_last`; all convolutions are stride 1, `valid`
padding, with bias.

| # | Layer        | Type          | Output shape | Weights (Keras layout)        | Activation |
|---|--------------|---------------|--------------|-------------------------------|------------|
| 0 | input_1      | Input         | 28×28×1      | —                             | —          |
| 1 | conv1        | Conv2D 5×5    | 24×24×3      | kernel [5][5][1][3], bias [3] | none       |
| 2 | hard_swish   | **HardSwish** | 24×24×3      | —                             | custom     |
| 3 | pool1        | MaxPool 2×2/2 | 12×12×3      | —                             | —          |
| 4 | conv2        | Conv2D 5×5    | 8×8×4        | kernel [5][5][3][4], bias [4] | ReLU       |
| 5 | pool2        | MaxPool 2×2/2 | 4×4×4        | —                             | —          |
| 6 | flatten      | Flatten       | 64           | —                             | —          |
| 7 | fc1          | Dense         | 22           | kernel [64][22], bias [22]    | ReLU       |
| 8 | fc_out       | Dense         | 10           | kernel [22][10], bias [10]    | none       |
| 9 | softmax      | Softmax       | 10           | —                             | softmax    |

Total parameters: **2042**.

### 3.2 Details that must match Keras exactly

- **HardSwish** (`model/custom_layers.py`): `y = x * relu6(x + 3) / 6`, where
  `relu6(v) = min(max(v, 0), 6)`. Element-wise, no weights.
- **Flatten order** is `channels_last`: `flat[(h*4 + w)*4 + c] = pool2[h][w][c]`.
- **Softmax** is part of the IP: the output is probabilities, not logits.

### 3.3 Reference accuracy

On `data/mnist_test_1000.npz` (first 1000 MNIST test images), the Keras model reaches
**96.70 %** top-1. The file also stores Keras outputs (`keras_probs`) as the golden
reference:

| Key           | Shape          | Type    | Meaning                                  |
|---------------|----------------|---------|------------------------------------------|
| `x`           | (1000, 28, 28) | uint8   | pixels; model input = `x / 255.0` (float32) |
| `y`           | (1000,)        | uint8   | labels                                   |
| `keras_probs` | (1000, 10)     | float32 | Keras softmax output                     |


## 4. Top-Level Interface (fixed — the Vivado design depends on it)

| Item              | Value                                                      |
|-------------------|------------------------------------------------------------|
| Top function      | `void lenet_axis(hls::stream<axis_t> &s_axis, hls::stream<axis_t> &m_axis)` |
| Stream word       | `typedef hls::axis<float, 0, 0, 0> axis_t;` — 32-bit IEEE-754 float |
| Interfaces        | `#pragma HLS INTERFACE axis port=s_axis` / `port=m_axis`   |
| Block control     | `#pragma HLS INTERFACE ap_ctrl_none port=return` (free-running, no AXI-Lite, no driver — same as `axis_filter`) |
| Clock / reset     | `ap_clk`, `ap_rst_n` (active-low)                          |
| IP VLNV           | `xilinx.com:hls:lenet_axis:1.0`                            |

**Protocol, per image:**

1. Read exactly **784** words from `s_axis`: pixel `(r, c)` is word `r*28 + c`,
   value `(float)pixel / 255.0f`. Ignore input `TKEEP`/`TLAST` (the DMA sets `TLAST` on word 784).
2. Write exactly **10** words to `m_axis`: probability of class 0…9, `keep = strb = 0xF`,
   **`last = 1` on the 10th word only** (AXI DMA S2MM completes on `TLAST`).
3. Wait for the next image. Back-to-back images must work without reset.

Use only **blocking** stream reads/writes. With `ap_ctrl_none`, C/RTL co-simulation
is only supported for designs with `hls::stream` ports and blocking accesses (UG1399).

This interface takes precedence over Knowledge Base rules that suggest otherwise
(e.g. `ap_ctrl_hs` at the top level, or non-blocking stream reads).


## 5. Requirements

### 5.1 Numerical

The internal data types are the designer's choice (fixed-point `ap_fixed` is
encouraged). The input/output stream stays float32.

| Check                              | Pass criterion                          |
|------------------------------------|-----------------------------------------|
| Top-1 agreement with Keras (argmax)| 20 / 20 testbench images                |
| Max \|p_hls − p_keras\| per entry  | ≤ 0.05                                  |

"Accuracy" in the report means these two checks. Running the C model on all 1000
images is optional. Fixed-point ranges may be calibrated on `data/mnist_test_1000.npz`;
no separate calibration set is provided.

### 5.2 Hardware

| Metric                         | Requirement                                     |
|--------------------------------|-------------------------------------------------|
| Estimated clock (csynth)       | ≤ 10 ns, no timing violation                    |
| LUT / FF / DSP / BRAM          | each ≤ 20 % of xczu3eg, csynth estimate (DSP ≤ 36 of 360). A small IP keeps the Vivado build short; prefer fewer parallel MACs over lower latency |
| Latency per image              | goal ≤ 20,000 cycles (200 µs @ 100 MHz), csynth worst case; report csynth and cosim latency |
| Deadlock warnings              | no `HLS 200-656` in the final csynth log — cosim PASS alone is not enough, the board runs far more images than cosim |

Correctness comes first. Design for these limits before the first csynth (§6 allows a
single csynth run); if the latency goal is not reached but §5.1 and the resource/timing
limits pass, export it anyway.


## 6. Flow & Deliverables

The flow runs to **cosim and IP export**, with one csynth run:

0. **Knowledge Base** (`/kb-skill`, read-only): Track 1 (similar past designs, type `cnn`)
   and Track 2 (rule library) before writing any code. Do not record anything in the KB.
1. **Extract** weights from the `.h5` with Python into `hls/lenet_weights.inc` (format
   is the designer's choice, e.g. float literals in Keras layout), and the first **20**
   images of `data/mnist_test_1000.npz` (pixels as uint8 integers, labels and
   `keras_probs`) into `hls/lenet_tb_data.inc`. Keep the extraction script as
   `hls/tools/extract_from_h5.py` (helper only, not an HLS design source).
2. **Write** the design: `hls/lenet.h`, `hls/lenet.cpp`, `hls/lenet_tb.cpp`. The
   testbench takes the number of images as an optional argument (`argv[1]`, default 20),
   calls `lenet_axis` once per image (back-to-back), checks `TLAST` on every 10th output
   word, checks §5.1 on those images, prints a PASS/FAIL summary and returns non-zero on
   failure.
3. **csim** (20 images) **→ csynth, once**. Re-run csynth only to fix a violation of
   §5.2 (resources, timing, `HLS 200-656`), at most once more; not to improve latency.
4. **cosim** on **2 images** (`cosim_design -tool xsim -argv 2`). Must PASS.
5. **Export**: `export_design -format ip_catalog -vendor xilinx.com -library hls -version 1.0`.
   Expected output: `hls/lenet_prj/solution1/impl/ip/` (contains `component.xml` and
   `xilinx_com_hls_lenet_axis_1_0.zip`).
6. **Report** in `hls/REPORT.md`, short (about 40 lines, no architecture essay): one results
   table (csim, csynth latency / LUT / FF / DSP / BRAM / estimated clock, cosim result and
   latency), data types in one line each, the Knowledge Base use (format in
   `.claude/skills/kb-skill/reference/kb-guide.md`, "Citing rules", applied rules only), and
   the final IP path. Take the numbers from the existing logs and reports; do not re-run
   any tool for the report.

All Tcl goes in `hls/run_hls.tcl`, with the steps as arguments
(e.g. `vitis_hls -f run_hls.tcl -tclargs csim csynth`, later `-tclargs cosim export`; if
`vitis_hls` is not installed, run the same script with `vitis-run --mode hls --tcl`);
project name `lenet_prj`, solution `solution1`. Add
`config_rtl -reset all -reset_level low`: a previous attempt on this board relied on
power-on register values and produced wrong results in hardware.

Test vectors go in `lenet_tb_data.inc`, not embedded in `lenet_tb.cpp`.

```
hls/
├── lenet.h  lenet.cpp  lenet_tb.cpp
├── lenet_weights.inc  lenet_tb_data.inc
├── run_hls.tcl
├── tools/extract_from_h5.py
├── REPORT.md
└── lenet_prj/solution1/impl/ip/      ← handed to Vivado (spec/hardware_spec.md)
```
