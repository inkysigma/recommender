"""Test our learner"""
import unittest
import tensorflow as tf
from recommender.learner.model import LearnerModel


class TestLearner(unittest.TestCase):
    """A collection of tests against the model to ensure it works"""

    def setUp(self):
        self.model = LearnerModel()

    def test_build(self):
        """Test whether the graph can be built correctly"""
        self.model.build_graph()

    def test_flush(self):
        """Test whether the graph can be run with a zero array"""
        self.model.build_graph()
        self.model.initialize()
        self.model.predict(tf.zeros([1, 1024]))

    def tearDown(self):
        self.model.close()

if __name__ == "__main__":
    unittest.main()
