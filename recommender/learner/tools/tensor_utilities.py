"""Some utilities for usage in tensor flow"""
import tensorflow as tf
from typing import List

def add_tensors(arr: List[tf.Tensor]):
    final = arr[0]
    for t in range(len(arr)):
        final = final + arr[t]
    return final 
