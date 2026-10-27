"""custom_layers.py — 隨模型附帶的自訂層定義 (sidecar)。

load 模型 (.h5) 前要先 import 本檔, 讓 @register_keras_serializable 標記的自訂層被註冊。
"""
import tensorflow as tf


@tf.keras.utils.register_keras_serializable(package='hls_custom')
class HardSwish(tf.keras.layers.Layer):
    """Hard-Swish 逐元素非線性: y = x * relu6(x + 3) / 6。

    shape-preserving (N->N)、無權重。
    """

    def call(self, inputs):
        return inputs * tf.nn.relu6(inputs + 3.0) / 6.0
