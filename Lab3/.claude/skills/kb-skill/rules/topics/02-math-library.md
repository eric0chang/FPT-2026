# Topic 2: Math library (4 rules)

Covers: hls_math, math.h/cmath functions, float vs fixed-point math. `must` / `must-not` first. Full rule: `../HLS/<ID>.md`.

| ID | Type | Summary | Tags |
|---|---|---|---|
| HLS-1301 | must | Fixed-point hls_math functions support only ap_fixed<W,I> with I<=33 and W-I<=32, ap_ufixed<W,I> with I<=32 and W-I<=32, ap_int<I> with I<=33, ap_uint<I> with I<=32, and do not support the Q, O, N template parameters. | ap_fixed, bit-width, fixed-point, math |
| HLS-1299 | pitfall | Mind float vs double in math calls: with C math.h, sqrt/sin/cos on float data build 64-bit double cores plus float-double converters (call sqrtf/sinf/cosf), and C90/C++ math.h copysign returns double; C++ <cmath> with namespace std avoids both. Watch mixed float/double expressions too. | area, double, float, math, type-conversion |
| HLS-1298 | recipe | To make C simulation match C/RTL co-simulation exactly for math functions in C++, include hls_math.h and call the hls:: versions, or add lib_hlsm.cpp as a design file; hls_math.h is not supported in C code. | cosim, csim, hls_math, math |
| HLS-1300 | direction | For math functions that have a fixed-point implementation, switching operands to ap_fixed gives smaller, faster RTL than floating point at slightly lower accuracy; re-run C simulation to confirm precision before synthesis. | ap_fixed, fixed-point, math, resource |
