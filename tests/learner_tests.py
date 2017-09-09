"""Test our learner"""
import unittest
import tensorflow as tf
import numpy as np
from recommender.learner.model import LearnerModel


class TestLearner(unittest.TestCase):
    """A collection of tests against the model to ensure it works"""

    def setUp(self):
        self.model = LearnerModel(categories=10)

    def test_build(self):
        """Test whether the graph can be built correctly"""
        self.model.build_graph()

    def tearDown(self):
        self.model.close()
        tf.reset_default_graph()


class TestPredictor(unittest.TestCase):
    def setUp(self):
        self.model = LearnerModel(categories=10, learning_rate=0.01, beta=0.005)
        self.model.build_graph()
        self.model.initialize()

    def test_train(self):
        """Test whether the model can be trained"""
        for _ in range(1, 20):
            self.model.train(np.zeros([1, 2048, 32]), np.zeros([1, 10]))

    def test_flush(self):
        """Test whether the graph can be run with a zero array"""
        result = self.model.predict(np.zeros([1, 2048, 32]))
        print(result)

    def test_predict(self):
        """Test whether the graph can be run with a zero array"""
        print()
        print("Testing the prediction:")
        print("Ensure that the second result is smaller than the first")
        result = self.model.predict(np.zeros([1, 2048, 32]))
        print(result)
        for _ in range(1, 20):
            self.model.train(np.zeros([10, 2048, 32]), np.zeros([10, 10]))
        result = self.model.predict(np.zeros([1, 2048, 32]))
        print(result)

    def tearDown(self):
        self.model.close()
        tf.reset_default_graph()


class TestSigmoid(unittest.TestCase):
    def setUp(self):
        self.model = LearnerModel(categories=10, use_sigmoid=True, learning_rate=1.5)
        self.model.build_graph()
        self.model.initialize()
        print("Testing sigmoid functionality")

    def test_sigmoid(self):
        print(self.model.predict(np.zeros([1, 2048, 32])))
        self.model.train(np.zeros([800, 2048, 32]), np.zeros([800, 10]))
        print(self.model.predict(np.zeros([1, 2048, 32])))

    def tearDown(self):
        self.model.close()
        tf.reset_default_graph()


class TestSave(unittest.TestCase):
    def setUp(self):
        self.model = LearnerModel(categories=10)
        self.model.build_graph()
        self.model.initialize()

    def test_save(self):
        print("Testing saving functionality")
        print(self.model.predict(np.zeros([1, 2048, 32])))
        self.model.train(np.zeros([800, 2048, 32]), np.zeros([800, 10]))
        print(self.model.predict(np.zeros([1, 2048, 32])))
        self.model.save("saved/test.model")
        self.model.close()
        tf.reset_default_graph()
        self.model = LearnerModel(categories=10)
        self.model.build_graph()
        self.model.load("saved/test.model-0")
        print(self.model.predict(np.zeros([1, 2048, 32])))

    def tearDown(self):
        self.model.close()
        tf.reset_default_graph()


if __name__ == "__main__":
    unittest.main()
