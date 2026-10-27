"""make_test_data.py — build data/mnist_test_1000.npz (first 1000 MNIST test images + Keras golden outputs).

  x           (1000, 28, 28) uint8    raw pixels; model input = x / 255.0 (float32)
  y           (1000,)        uint8    true labels
  keras_probs (1000, 10)     float32  softmax output of model/custom_lenet_model.h5

Run: python make_test_data.py --mnist-dir <dir with x_test.npy, y_test.npy>
"""
import argparse
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(HERE, os.pardir, 'model')
N = 1000

ap = argparse.ArgumentParser()
ap.add_argument('--mnist-dir', required=True)
args = ap.parse_args()

sys.path.insert(0, MODEL_DIR)
import tensorflow as tf
from custom_layers import HardSwish  # noqa: F401  (registers the custom layer)

x = np.load(os.path.join(args.mnist_dir, 'x_test.npy'))[:N]   # float32 in [0,1], (N,28,28,1)
y = np.load(os.path.join(args.mnist_dir, 'y_test.npy'))[:N]
x_u8 = np.rint(x * 255.0).astype(np.uint8)
assert np.array_equal(x_u8.astype(np.float32) / 255.0, x), 'pixels are not exact k/255 values'

model = tf.keras.models.load_model(os.path.join(MODEL_DIR, 'custom_lenet_model.h5'), compile=False)
probs = model.predict(x, verbose=0).astype(np.float32)

out = os.path.join(HERE, 'mnist_test_1000.npz')
np.savez_compressed(out, x=x_u8[..., 0], y=y.astype(np.uint8), keras_probs=probs)
print(f'saved {out}  keras top-1 accuracy = {(probs.argmax(1) == y).mean():.4f}')
