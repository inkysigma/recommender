"""A module for creating training models to train over tracks."""
from typing import Callable
import tensorflow as tf


class Learner:
    """A learner for training over the model."""

    def __init__(self,
                 activation_function: Callable[tf.Tensor, tf.Tensor]=tf.nn.relu,
                 name: str="track-learner"):
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
            0, dtype=int32, trainable=False, name="global_step")

        # Specify that the graph is unbuilt
        self.__graph_built__ = False

    def train(self, batch, y):
        if not self.__graph_built__:
            build_graph()
        pass

    def test(self, batch, y):
        pass

    def load(self, file: str):
        """
        Loads all the variables from the 
        """

    def load_saved(self, name: str) -> None:
        if self.__graph_built__:
            return

        self.__graph_built__ = True

    def build_graph(self):
        """
        Builds the variables in the graph. Should be called before running
        Args:
            batch_size (int): the number of batches passed in per train or test
        """

        # Inputs to our models
        X_ = tf.placeholder(dtype=tf.float32, shape=(None, 1024), name="X_")

        # Target outputs of our model
        y_ = tf.placeholder(dtype=tf.float32, shape=(None, 1), name="y_")

        conv1 = tf.nn.conv1d(placeholders, filters=32, stride=10, padding="SAME", name="conv1")

    def initialize(self):
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
            return temp_session.run(self.global_step)

    def predict(self, batch):
        pass
