"""A module for creating training models to train over tracks."""
from typing import Callable
from recommender.learner.tools.tensor_utilities import add_tensors, create_bias, create_weight
import tensorflow as tf
import numpy as np
import logging


class LearnerModel:
    """A learner for training over the model."""

    def __init__(self,
                 categories: int,
                 logger: logging.Logger,
                 summary: tf.summary.FileWriter = None,
                 activation_function: Callable[[tf.Tensor], tf.Tensor] = tf.nn.relu,
                 beta: float = 0.01,
                 frames: int = 2048,
                 channels: int = 32,
                 dropout: bool = True,
                 use_sigmoid: bool = False,
                 learning_rate: float = 0.05):
        """
        Creates a learner with the given activation function and name.
        Args:
            activation_function (Callable[tf.Tensor, None]): an activation function
                for the network. default is tf.ReLu
            logger (logging.Logger): the logger to use to track changes
            summary (tf.summary.FileWriter): the file writer to save TensorFlow summaries
            categories (int): the number of target categories
            beta (float): the regularization constant
            frames (int): the number of frames in each track
            channels (int): the number of channels in each track. This should be
                equivalent to n_mfcc for the number of coefficients.
            dropout (bool): whether to enable the dropout layer
            use_sigmoid (bool): use sigmoid read out instead of SoftMax
        """
        self.__summary_writer__ = summary

        self.__learning_rate__ = learning_rate
        self.acf = activation_function

        # Create session and initialize it
        self.sess = tf.Session()
        self.sess.as_default()

        # Create the graph necessary
        self.graph = tf.Graph()
        self.graph.as_default()

        # Create a counter for global_steps
        self.global_step = tf.Variable(
            0, dtype=tf.int32, trainable=False, name="global_step")

        # Specify that the graph is unbuilt
        self.__graph_built__ = False

        self.__frames__ = frames
        self.__channels__ = channels

        # Create a system of weights and biases
        self.__initialize_variables__()

        self.__categories__ = categories

        self.__beta__ = beta

        self.__dropout__ = dropout

        # Initialize inputs to the system

        # Inputs to our models
        self.input = tf.placeholder(
            dtype=tf.float32, shape=(None, self.__frames__, channels), name="X")

        # Target outputs of our model
        self.y = tf.placeholder(dtype=tf.float32, shape=(
            None, self.__categories__), name="y")

        self.__use_sigmoid__ = use_sigmoid

        self.__final_logits__ = None
        self.__final_regularization__ = None

        self.__logger__ = logger

    def __initialize_variables__(self):
        """Initialize the variables needed to multiply matricies and add biases"""
        self.__weights__ = []
        self.__biases__ = []
        n = 1
        while n < self.__frames__ // 4:
            n *= 2

        self.__weights__.append(
            create_weight([self.__frames__ // 4, n]))
        self.__biases__.append(create_bias([n]))

        while n > 1024:
            self.__weights__.append(create_weight([n, n // 2]))
            self.__biases__.append(create_bias([n // 2]))
            n //= 2

        if n < 1024:
            self.__weights__.append(create_weight([n, 1024]))
            self.__biases__.append(create_bias([1024]))

        self.__weights__.extend([
            create_weight([1024, 512]),
            create_weight([512, 256]),
            create_weight([256, 128]),
            create_weight([128, 64]),
            create_weight([64, 64])
        ])
        self.__biases__.extend([
            create_bias([512]),
            create_bias([256]),
            create_bias([128]),
            create_bias([64]),
            create_bias([64])
        ])

    def train(self, batch, y):
        """
        Train the model given a batch and a set of y.
        Args:
            batch (np.ndarray): a batch representing the possible input.
                Should have size [batch_size, frames, channels]
            y (np.ndarray): an representing the target outputs.
                Should have size [batch_size, categories]
        """
        if not self.__graph_built__:
            self.build_graph()
        if not self.__use_sigmoid__:
            error = tf.nn.softmax_cross_entropy_with_logits(
                labels=self.y, logits=self.__final_logits__
            )
        else:
            error = tf.nn.sigmoid_cross_entropy_with_logits(
                labels=self.y, logits=self.__final_logits__
            )

        # Add regularization terms
        error = error + self.__beta__ * self.__final_regularization__

        cross_entropy = tf.reduce_mean(error)
        train_step = tf.train.GradientDescentOptimizer(
            self.__learning_rate__).minimize(cross_entropy)
        train_step.run(feed_dict={self.input: batch,
                                  self.y: y}, session=self.sess)

    def test(self, batch, y) -> float:
        prediction = self.predict(batch)
        return tf.nn.l2_loss(batch, y)

    def load(self, file: str):
        """
        Loads all the variables from a file
        """
        saver = tf.train.Saver()
        saver.restore(self.sess, file)

    def build_graph(self) -> None:
        """
        Builds the variables in the graph. Should be called before running.
        """

        conv1 = tf.layers.conv1d(self.input, filters=32, strides=1, kernel_size=4,
                                 padding="SAME", name="conv1", activation=self.acf)

        maxpool1 = tf.nn.max_pool(tf.reshape(conv1, [-1, 1, self.__frames__, self.__channels__]),
                                  ksize=[1, 1, 16, 1], strides=[1, 1, 4, 1],
                                  padding="SAME", name="maxpool1")

        reduce1 = tf.reduce_max(maxpool1, axis=[3])

        if self.__dropout__:
            dropout1 = tf.nn.dropout(reduce1, keep_prob=0.4)
        else:
            dropout1 = reduce1

        result1 = self.acf(dropout1)

        assert len(self.__weights__) == len(self.__biases__)

        prev_layer = tf.reshape(result1, [-1, self.__frames__ // 4])
        for i in range(len(self.__weights__)):
            prev_layer = self.acf(
                tf.matmul(prev_layer, self.__weights__[i]) + self.__biases__[i])

        final_weight = create_weight(
            [64, self.__categories__], name="final_weight")
        final_biases = create_bias(
            [self.__categories__], name="final_bias")

        self.__final_logits__ = tf.matmul(
            prev_layer, final_weight) + final_biases

        self.__final_regularization__ = tf.nn.l2_loss(final_weight) \
                                        + add_tensors([tf.nn.l2_loss(w) for w in self.__weights__])
        self.__graph_built__ = True

    def initialize(self):
        """Initialize the global variables of the graph"""
        self.sess.run(tf.global_variables_initializer())

    def save(self, file: str):
        """
        Saves the session to the specified file
        Args:
            file (str): the name of the file
        """
        saver = tf.train.Saver()
        saver.save(self.sess, file, global_step=self.global_step)

    def get_global_steps(self) -> int:
        """
        Gets the number of global steps currently in the session.
        Returns:
            int: the number of global steps performed
        """
        return self.sess.run(self.global_step)

    def predict(self, batch: np.array):
        """
        Predict the result of some observations
        Args:
            batch (np.array): a tensor of shape (batch_size, 1024)
        Returns:
            list: a list representing the predicted results.
        """
        if not self.__use_sigmoid__:
            return self.sess.run(tf.nn.softmax(self.__final_logits__, name="predict_logits_softmax"),
                                 feed_dict={self.input: batch})
        else:
            return self.sess.run(tf.nn.sigmoid(self.__final_logits__, name="predict_logits_sigmoid"),
                                 feed_dict={self.input: batch})

    def close(self):
        self.sess.close()
