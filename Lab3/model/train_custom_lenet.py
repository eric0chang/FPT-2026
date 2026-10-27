"""train_custom_lenet.py — mini LeNet, 但 conv1 的 ReLU 換成自訂層 HardSwish。

  Conv2D(3,5x5) -> HardSwish(custom) -> MaxPool -> Conv2D(4,5x5,relu) -> MaxPool
  -> Flatten -> Dense(22,relu) -> Dense(10) -> Softmax

資料沿用 ../model_training/ 的 MNIST .npy (不重新下載)。所有輸出都留在本資料夾。
Run: python train_custom_lenet.py   (TensorFlow 2.x)
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault('KERAS_HOME', os.path.join(HERE, '.keras'))  # keep Keras config inside tutorial/

import numpy as np
import tensorflow as tf
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Input, Conv2D, MaxPooling2D, Flatten, Dense, Softmax

from custom_layers import HardSwish

np.random.seed(0)
tf.random.set_seed(0)

DATA = os.path.join(HERE, os.pardir, 'model_training')
x_train = np.load(os.path.join(DATA, 'x_train.npy'))
y_train = np.load(os.path.join(DATA, 'y_train.npy'))
x_test = np.load(os.path.join(DATA, 'x_test.npy'))
y_test = np.load(os.path.join(DATA, 'y_test.npy'))

model = Sequential([
    Input(shape=(28, 28, 1), name='input_1'),
    Conv2D(3, (5, 5), padding='valid', name='conv1'),   # 不帶 activation, 交給 HardSwish
    HardSwish(name='hard_swish'),
    MaxPooling2D((2, 2), name='pool1'),
    Conv2D(4, (5, 5), padding='valid', activation='relu', name='conv2'),
    MaxPooling2D((2, 2), name='pool2'),
    Flatten(name='flatten'),
    Dense(22, activation='relu', name='fc1'),
    Dense(10, name='fc_out'),
    Softmax(name='softmax'),
])
model.summary()
print(f'[info] total params = {model.count_params()}')

model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
model.fit(x_train, y_train, batch_size=128, epochs=12, validation_split=0.1, verbose=2)

test_loss, test_acc = model.evaluate(x_test, y_test, verbose=0)
print(f'[info] test accuracy = {test_acc:.4f}')

out = os.path.join(HERE, 'custom_lenet_model.h5')
model.save(out)

# reload check: 自訂層能正確存/讀, 輸出一致
reloaded = tf.keras.models.load_model(out, compile=False)
diff = float(np.max(np.abs(model.predict(x_test[:100], verbose=0) - reloaded.predict(x_test[:100], verbose=0))))
print('[info] saved', out, ' reload max|diff| =', diff)
