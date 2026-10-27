# LeNet HLS IP to Hardware — Prompt Library

---

## 1. Build the HLS IP and the bitstream

```
/kb-skill
Convert the Keras model model/custom_lenet_model.h5 (custom layer in
model/custom_layers.py) into a Vitis HLS IP according to spec/hls_spec.md.
Write the HLS C++ from scratch, using the HLS Knowledge Base.
Then swap the IP into the Lab2 block design according to spec/hardware_spec.md,
build through bitstream and report timing.
```

---

## 2. Verify on Hardware

```
Provide a PYNQ jupyter notebook that runs LeNet inference on the AUP-ZU3
with pynq/lenet.bit, using the images in data/mnist_test_1000.npz, and
compares the board output with keras_probs.
And write markdown description in notebook.
```

---
