"""A module for creating training models to train over tracks."""
from typing import Callable
from recommender.learner.tools.tensor_utilities import add_tensors
import tensorflow as tf
import numpy as np


class LearnerModel:
    """A learner for training over the model."""

    def __init__(self,
                 categories: int,
                 activation_function: Callable[[tf.Tensor], tf.Tensor]=tf.nn.relu,
                 beta: float = 0.01,
                 name: str = "track-learner"):
        """
        Creates a learner with the given activation function and name.
        Args:
            activation_function (Callable[tf.Tensor, None]): an activation function
                for the network. default is tf.ReLu
            name (str): the name of the learner
                default is track-learner
        """
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

        # Create a system of weights and biases
        self.__initialize_variables__()

        self.__categories__ = categories

        self.__beta__ = beta

    def __initialize_variables__(self):
        """Initialize the variables needed to multiply matricies and add biases"""
        self.__weights__ = [
            self.__create_weight__([1024, 512]),
            self.__create_weight__([512, 256]),
            self.__create_weight__([256, 128]),
            self.__create_weight__([128, 64]),
            self.__create_weight__([64, 64])
        ]
        self.__biases__ = [
            self.__create_bias__([512]),
            self.__create_bias__([256]),
            self.__create_bias__([128]),
            self.__create_bias__([64]),
            self.__create_bias__([64])
        ]

    def __create_weight__(self, shape, name: str=None):
        return tf.Variable(tf.truncated_normal(shape=shape, stddev=0.1), name=name)

    def __create_bias__(self, shape, name: str=None):
        return tf.Variable(tf.constant(0.2, shape=shape), name=name)

    def train(self, batch, y):
        if not self.__graph_built__:
            self.build_graph()
        cross_entropy = tf.reduce_mean(
            tf.nn.softmax_cross_entropy_with_logits(
                labels=self.y, logits=self.__final_logits__)
            + self.__beta__ * self.__final_regularization__)
        train_step = tf.train.GradientDescentOptimizer(
            0.01).minimize(cross_entropy)
        train_step.run(feed_dict={self.input: batch,
                                  self.y: y}, session=self.sess)

    def test(self, batch, y):
        pass

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

        # Inputs to our models
        self.input = tf.placeholder(
            dtype=tf.float32, shape=(None, 1024, 1), name="X")

        # Batch size
        batch_size = tf.shape(self.input)[0]

        # Target outputs of our model
        self.y = tf.placeholder(dtype=tf.float32, shape=(
            None, self.__categories__), name="y")

        conv1 = tf.layers.conv1d(self.input, filters=16, strides=1, kernel_size=4,
                                 padding="SAME", name="conv1", activation=self.acf)

        maxpool1 = tf.nn.max_pool(tf.reshape(conv1, [-1, 1, 1024, 16]), ksize=[1, 1, 16, 1], strides=[
                                  1, 1, 1, 1], padding="SAME", name="maxpool1")

        reduce1 = tf.reduce_max(maxpool1, axis=[3])

        dropout1 = tf.nn.dropout(reduce1, keep_prob=0.4)

        result1 = self.acf(dropout1)

        assert len(self.__weights__) == len(self.__biases__)

        prev_layer = tf.reshape(result1, [-1, 1024])
        for i in range(len(self.__weights__)):
            prev_layer = self.acf(
                tf.matmul(prev_layer, self.__weights__[i]) + self.__biases__[i])

        final_weight = self.__create_weight__(
            [64, self.__categories__], name="final_weight")
        final_biases = self.__create_bias__(
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
        saver = tf.train.Saver(var_list=tf.trainable_variables())
        saver.save(self.sess, file, global_step=self.global_step)

    def get_global_steps(self) -> int:
        """Gets the number of global steps currently in the session."""
        return self.sess.run(self.global_step)

    def predict(self, batch: np.array):
        """
        Predict the result of some observations
        Args:
            batch (np.array): a tensor of shape (batch_size, 1024)
        Returns:
            list: a list representing the predicted results.
        """
        return self.sess.run(tf.nn.softmax(self.__final_logits__, name="predict-logits"), feed_dict={self.input: batch})

    def close(self):
        self.sess.close()
