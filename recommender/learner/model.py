"""A module for creating training models to train over tracks."""
from typing import Callable
import tensorflow as tf


class LearnerModel:
    """A learner for training over the model."""

    def __init__(self,
                 activation_function: Callable[tf.Tensor, tf.Tensor]=tf.nn.relu,
                 name: str="track-learner",
                 categories: int= 10):
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
        return tf.Variable(tf.truncated_normal(shape, stddev=0.1), name=name)

    def __create_bias__(self, shape, name:str=None):
        return tf.Variable(tf.constant(0.2, shape), name=name)

    def train(self, batch, y):
        if not self.__graph_built__:
            self.build_graph()
        cross_entropy = tf.reduce_mean(
            tf.nn.softmax_cross_entropy_with_logits(labels=self.y, logits=self.__final_layer__))
        train_step = tf.train.GradientDescentOptimizer(
            0.5).minimize(cross_entropy)
        train_step.run(feed_dict={self.X: batch, self.y: y})

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
        self.X = tf.placeholder(dtype=tf.float32, shape=(None, 1024), name="X")

        # Batch size
        batch_size = tf.shape(self.X)[0]

        # Target outputs of our model
        self.y = tf.placeholder(dtype=tf.float32, shape=(None, 1), name="y")

        conv1 = tf.nn.conv1d(self.X, filters=32, stride=10,
                             padding="SAME", name="conv1")

        maxpool1 = tf.nn.max_pool(conv1, ksize=[batch_size, 1, 1024, 1], strides=[
                                  1, 1, 5, 1], padding="SAME", name="maxpool1")

        dropout1 = tf.nn.dropout(maxpool1, keep_prob=0.4)

        result1 = self.acf(dropout1)

        assert len(self.__weights__) == len(self.__biases__)
        prev_layer = result1
        for i in len(self.__weights__):
            prev_layer = self.acf(
                tf.matmul(prev_layer, self.__weights__[i]) + self.__biases__[i])

        final_weight = self.__create_weight__([64, self.__categories__], name="final_weight")
        final_biases = self.__create_bias__([64], name="final_bias")

        self.__final_layer__ = tf.matmul(
            prev_layer, final_weight) + final_biases
        self.__graph_built__ = True

    def initialize(self):
        """Initialize the global variables of the graph"""
        tf.global_variables_initializer()

    def save(self, file: str):
        """
        Saves the session to the specified file
        Args:
            file (str): the name of the file
        """
        saver = tf.train.Saver(var_list=tf.trainable_variables())
        saver.save(self.sess, file, global_step=self.global_step)

    def get_global_steps(self) -> int:
        with tf.Session() as temp_sess:
            return temp_sess.run(self.global_step)

    def predict(self, batch):
        pass

    def close(self):
        self.sess.close()
