from keras.layers import Conv2D, BatchNormalization, Activation, MaxPooling2D
from keras.layers import Add
from keras.initializers import glorot_uniform
import tensorflow as tf
import keras.backend as K
import numpy as np
K.set_image_data_format("channels_last")


def convolutional_block(X, f, filters, stage, block, s=2):
    """
    Implementation of the convolutional block as defined in Figure 4

    Arguments:
    X -- input tensor of shape (m, n_H_prev, n_W_prev, n_C_prev)
    f -- integer, specifying the shape of the middle CONV's window for the main path
    filters -- python list of integers, defining the number of filters in the CONV layers of the main path
    stage -- integer, used to name the layers, depending on their position in the network
    block -- string/character, used to name the layers, depending on their position in the network
    s -- Integer, specifying the stride to be used

    Returns:
    X -- output of the convolutional block, tensor of shape (n_H, n_W, n_C)
    """

    # defining name basis
    conv_name_base = 'res' + str(stage) + block + '_branch'
    bn_name_base = 'bn' + str(stage) + block + '_branch'

    # Retrieve Filters
    F1, F2, F3 = filters

    # Save the input value
    X_shortcut = X

    # MAIN PATH
    # First component of main path
    X = Conv2D(F1, (1, 1), strides=(s, s), padding="valid", name=conv_name_base + '2a',
               kernel_initializer=glorot_uniform(seed=0))(X)
    X = BatchNormalization(axis=3, name=bn_name_base + '2a')(X)
    X = Activation('relu')(X)

    # Second component of main path
    X = Conv2D(F2, (f, f), strides=(1, 1), padding="same", name=conv_name_base + "2b",
               kernel_initializer=glorot_uniform(seed=0))(X)
    X = BatchNormalization(axis=3, name=bn_name_base + "2b")(X)
    X = Activation("relu")(X)

    # Third component of main path
    X = Conv2D(F3, (1, 1), strides=(1, 1), padding="valid", name=conv_name_base + "2c",
               kernel_initializer=glorot_uniform(seed=0))(X)
    X = BatchNormalization(axis=3, name=bn_name_base + "2c")(X)

    # SHORTCUT PATH
    X_shortcut = Conv2D(F3, (1, 1), strides=(s, s), padding="valid", kernel_initializer=glorot_uniform(seed=0),
                        name=conv_name_base + "1")(X_shortcut)
    X_shortcut = BatchNormalization(axis=3, name=bn_name_base + "1")(X_shortcut)

    # Final step: Add shortcut value to main path, and pass it through a RELU activation
    X = Add()([X, X_shortcut])
    X = Activation("relu")(X)

    return X


if __name__ == "__main__":
    np.random.seed(1)
    A_prev = tf.placeholder(dtype=tf.float32, shape=[3, 4, 4, 6])
    X = np.random.randn(3, 4, 4, 6)
    A = convolutional_block(A_prev, 2, [2, 4, 6], 1, "a")
    sess = tf.Session()
    sess.run(tf.global_variables_initializer())
    A_value = sess.run(A, feed_dict={A_prev: X})
    print(A_value[1, 1, 0])
    sess.close()