"""A module for creating training models to train over tracks."""
from typing import Callable
from recommender.learner.tools.tensor_utilities import add_tensors
import tensorflow as tf
import numpy as np


class LearnerModel:
    """A learner for training over the model."""

    def __init__(self,
                 categories: int,
                 activation_function: Callable[[tf.Tensor], tf.Tensor] = tf.nn.relu,
                 beta: float = 0.01,
                 frames: int = 2048,
                 channels: int = 32,
                 dropout: bool = True,
                 use_sigmoid: bool = False,
                 learning_rate: float=0.05):
        """
        Creates a learner with the given activation function and name.
        Args:
            activation_function (Callable[tf.Tensor, None]): an activation function
                for the network. default is tf.ReLu
            name (str): the name of the learner
                default is track-learner
            categories (int): the number of target categories
            beta (float): the regularization constant
            frames (int): the number of frames in each track
            channels (int): the number of channels in each track. This should be
                equivalent to n_mfcc for the number of coefficients.
            dropout (bool): whether to enable the dropout layer
            use_sigmoid (bool): use sigmoid read out instead of SoftMax
        """
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

    def __initialize_variables__(self):
        """Initialize the variables needed to multiply matricies and add biases"""
        self.__weights__ = []
        self.__biases__ = []
        n = 1
        while n < self.__frames__ // 4:
            n *= 2

        self.__weights__.append(
            self.__create_weight__([self.__frames__ // 4, n]))
        self.__biases__.append(self.__create_bias__([n]))

        while n > 1024:
            self.__weights__.append(self.__create_weight__([n, n // 2]))
            self.__biases__.append(self.__create_bias__([n // 2]))
            n //= 2

        if n < 1024:
            self.__weights__.append(self.__create_weight__([n, 1024]))
            self.__biases__.append(self.__create_bias__([1024]))

        self.__weights__.extend([
            self.__create_weight__([1024, 512]),
            self.__create_weight__([512, 256]),
            self.__create_weight__([256, 128]),
            self.__create_weight__([128, 64]),
            self.__create_weight__([64, 64])
        ])
        self.__biases__.extend([
            self.__create_bias__([512]),
            self.__create_bias__([256]),
            self.__create_bias__([128]),
            self.__create_bias__([64]),
            self.__create_bias__([64])
        ])

    def __create_weight__(self, shape, name: str = None):
        """
        Create a weight of the given shape and name
        Args:
            shape: an n-dimensional list of integers representing the shape
            name: the name of the operation to process
        """
        return tf.Variable(tf.truncated_normal(shape=shape, stddev=0.1), name=name)

    @staticmethod
    def __create_bias__(shape, name: str = None):
        return tf.Variable(tf.constant(0.2, shape=shape), name=name)

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
        error = None
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

        conv1 = tf.layers.conv1d(self.input, filters=32, strides=1, kernel_size=4,
                                 padding="SAME", name="conv1", activation=self.acf)

        maxpool1 = tf.nn.max_pool(tf.reshape(conv1, [-1, 1, self.__frames__, self.__channels__]),
                                  ksize=[1, 1, 16, 1], strides=[1, 1, 4, 1],
                                  padding="SAME", name="maxpool1")

        reduce1 = tf.reduce_max(maxpool1, axis=[3])

        if self.__dropout__:
            dropout1 = tf.nn.dropout(reduce1, keep_prob=0.4)

        result1 = self.acf(dropout1)

        assert len(self.__weights__) == len(self.__biases__)

        prev_layer = tf.reshape(result1, [-1, self.__frames__ // 4])
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
