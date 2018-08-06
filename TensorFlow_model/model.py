from TensorFlow_model.toolkit import *

with tf.Graph().as_default():  # 构建计算图

    # 构建输入占位符, 分别为图像 标签 学习率
    with tf.name_scope("Inputs"):
        x = tf.placeholder(shape=(Config.batch_size, Config.height, Config.width, Config.channels),
                           dtype=tf.float32, name="images")
        y = tf.placeholder(shape=(Config.batch_size, ), dtype=tf.int32, name="labels")
        learning_rate = tf.placeholder(shape=[], dtype=tf.float32, name="learning_rate")

    # 构建前向传播
    with tf.name_scope("Forward_propagation"):

        # 0填充
        with tf.name_scope("Zero_padding"):
            paddings = np.ones(shape=(4, 2)) * 3
            paddings[0, :] = 0   # 只填充图像的height
            paddings[-1, :] = 0  # 只填充图像的width
            x = tf.pad(x, paddings=paddings)

        # stage1
        with tf.name_scope("Stage_1"):
            with tf.name_scope("Conv_1"):
                x = conv2d(x, filters_h=7, num_filters=64, strides=2, padding="VALID")
            with tf.name_scope("BN_1"):
                x = tf.layers.batch_normalization(x, training=True)
            with tf.name_scope("Relu"):
                x = tf.nn.relu(x)
            with tf.name_scope("Max_pool"):
                x = tf.nn.max_pool(x, ksize=[1, 3, 3, 1], strides=[1, 2, 2, 1], padding="VALID")

        # stage2
        with tf.name_scope("Stage_2"):
            with tf.name_scope("Conv_block_1"):
                x = convolution_block(x, num_filters=[64, 64, 256], f=3, s=1)
            with tf.name_scope("Identity_block_1"):
                x = identity_block(x, num_filters=[64, 64, 256])
            with tf.name_scope("Identity_block_2"):
                x = identity_block(x, num_filters=[64, 64, 256])

        # stage3
        with tf.name_scope("Stage_3"):
            with tf.name_scope("Conv_block_1"):
                x = convolution_block(x, num_filters=[128, 128, 512])
            with tf.name_scope("Identity_block_1"):
                x = identity_block(x, num_filters=[128, 128, 512])
            with tf.name_scope("Identity_block_2"):
                x = identity_block(x, num_filters=[128, 128, 512])
            with tf.name_scope("identity_block_3"):
                x = identity_block(x, num_filters=[128, 128, 512])

        # stage4
        with tf.name_scope("Stage_4"):
            with tf.name_scope("Conv_block_1"):
                x = convolution_block(x, num_filters=[256, 256, 1024])
            with tf.name_scope("Identity_block_1"):
                x = identity_block(x, num_filters=[256, 256, 1024])
            with tf.name_scope("Identity_block_2"):
                x = identity_block(x, num_filters=[256, 256, 1024])
            with tf.name_scope("identity_block_3"):
                x = identity_block(x, num_filters=[256, 256, 1024])
            with tf.name_scope("Identity_block_4"):
                x = identity_block(x, num_filters=[256, 256, 1024])
            with tf.name_scope("identity_block_5"):
                x = identity_block(x, num_filters=[256, 256, 1024])

        # stage5
        with tf.name_scope("Stage_5"):
            with tf.name_scope("Conv_block_1"):
                x = convolution_block(x, num_filters=[512, 512, 2048])
            with tf.name_scope("Identity_block_1"):
                x = identity_block(x, num_filters=[512, 512, 2048])
            with tf.name_scope("Identity_block_2"):
                x = identity_block(x, num_filters=[512, 512, 2048])

        # Average pool
        x = tf.nn.avg_pool(x, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding="VALID")

        # Flatten
        with tf.name_scope("Flatten"):
            x_flatten = flatten(x)

        # 全连接层
        with tf.name_scope("Fully_connected"):
            logits = fully_connected(x_flatten)

        # softmax层
        with tf.name_scope("Softmax"):
            prediction = tf.nn.softmax(logits=logits)

    # 构建损失
    with tf.name_scope("Loss"):
        loss = tf.reduce_mean(tf.nn.sparse_softmax_cross_entropy_with_logits(logits=logits, labels=y),
                              name="cross_entropy")

    # 构建优化器
    # 这一步现需要先计算 mean 和 stddev 的滑动平均
    with tf.name_scope("Train"):
        update_ops = tf.get_collection(tf.GraphKeys.UPDATE_OPS)
        optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate)
        with tf.control_dependencies(update_ops):
            train_op = optimizer.minimize(loss=loss)

    # 构建评估节点
    with tf.name_scope("Evaluate"):
        bool_list = tf.nn.in_top_k(predictions=logits, targets=y, k=1)
        accuracy = tf.reduce_mean(tf.cast(bool_list, tf.float32))

    # 存放计算图
    writer = tf.summary.FileWriter(logdir=Config.logdir, graph=tf.get_default_graph())
    writer.close()






