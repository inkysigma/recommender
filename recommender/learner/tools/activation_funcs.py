"""Alternative activation functions for the neural network"""
import tensorflow as tf

def prelu(alpha: float = 0.01):
    """
    Returns a function constructed on the PReLU activation function
    Args:
        alpha (float): a float representing the constant to multiply by
    """
    def __prelu__(_x):
        return tf.maximum(0.0, _x) + alpha * tf.minimum(0.0, _x)
    return __prelu__
