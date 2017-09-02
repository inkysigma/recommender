"""
Some utilities for usage in managing tensors. This includes various operations
on lists of tensors such as add_tensors.
"""
from typing import List
import tensorflow as tf


def add_tensors(arr: List[tf.Tensor]):
    """
    Add a list of tensors into a tensor. Analogous to the sum() method for int
    Args:
        arr (List[tf.Tensor]): the array to sum over

    Returns:
        tf.Tensor: a tensor representing the sum of the tensors
    """
    final = arr[0]
    for _, item in enumerate(arr, 1):
        final = final + item
    return final


def list_to_sparse(mapping: List[str], targets: List[str], consistent=True) -> List[tf.Tensor]:
    """
    Maps a list of targets to a SpareTensor based on a list.
    Args:
        mapping (List[str]): a map of all possible targets of the sparse tensor.
        tagets (List[str]): a list of the targets which will be converted to tensors
        consistent (bool): whether or not the map is already in order.
            If true, the map will not be pre-sorted. It is recommended to sort in order
            to preserve order between mappings

    Returns:
        List[tf.Tensor]
    """
    output_size = len(mapping)
    tensors = []
    sorted_mapping = mapping
    if not consistent:
        sorted_mapping = sorted(mapping)
    for target in targets:
        tensors.append(tf.SparseTensor(
            indices=[[sorted_mapping.index(i) for i in sorted_mapping]],
            values=[1 for i in range(len(targets))],
            dense_shape=[output_size]))
    return tensors


def concat_sp_tensors_1D(tensors: List[tf.Tensor]) -> tf.Tensor:
    """
    Concatenates a list of 1D sparse tensors along the x-axis
    Args:
        tensors (List[tf.Tensor]): the list of tensors to concatenate

    Returns:
        tf.Tensor: a tensor representing the sum
    """
    return tf.sparse_concat(sp_inputs=tensors, axis=0)


def create_weight(shape, deviation: float, name: str = None) -> tf.Variable:
    """
    Create a TensorFlow weight with the provided shape. The weight
    is trainable and uses a truncated_normal generation of values.
    Args:
        shape (List[int]): a list of integers representing the shape of the tensor.
        deviation (float): the number of standard deviations
        name (str): the name of the variable

    Returns:
        tf.Tensor: the weight created as a tensor
    """
    return tf.Variable(tf.truncated_normal(shape=shape, stddev=deviation), name=name)


def create_bias(shape, constant: float = 0.2, name: str = None) -> tf.Variable:
    """
    Creates a bias variable with the provided shape. The bias is trainable and uses
    a constant to initialize the value.
    Args:
        shape (List[int]): a list of integers representing the shape of the tensor.
        constant (float): the constant to initialize the bias to
        name: the name of the variable

    Returns:
        tf.Tensor: the bias represented as a tensor
    """
    return tf.Variable(tf.constant(constant, shape=shape), name=name)
