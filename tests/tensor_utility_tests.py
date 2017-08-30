"""Tests on the tensor utilities module"""
import unittest
import random
import recommender.learner.tools.tensor_utilities as util
import tensorflow as tf

class TensorUtilityTest(unittest.TestCase):
    def test_concat_1d(self):
        with tf.Session() as sess:
            tensors = [tf.SparseTensor(indices=[[1, i]], values=[i], dense_shape=[1, 10])
                       for i in range(0, 9)]
            tensor = util.concat_sp_tensors_1D(tensors)
            print(sess.run(tensor))


if __name__ == "__main__":
    unittest.main()
